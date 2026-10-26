import hashlib
import hmac
import os

import requests
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .catalogo_client import CatalogoError, consolidar, liberar
from .models import Order, PaymentWebhookEvent
from .payment_client import PaymentError, crear_checkout


def _usuario_autenticado(request):
    auth = request.headers.get("Authorization", "")
    if not auth.lower().startswith("token "):
        return None

    url = os.environ.get("GESTION_VERIFY_TOKEN_URL", "")
    if not url:
        return None

    try:
        response = requests.get(
            url,
            headers={"Authorization": auth, "Accept": "application/json"},
            timeout=5,
        )
        if response.status_code != 200:
            return None
        data = response.json()
        user = data.get("usuario", {})
        if not data.get("valido") or str(user.get("estado", "")).lower() != "activo":
            return None
        return user.get("id")
    except (requests.RequestException, ValueError, AttributeError):
        return None


class IniciarPagoView(APIView):
    permission_classes = []

    def post(self, request, pk):
        cliente_id = _usuario_autenticado(request)
        if not cliente_id:
            return Response({"error": "Autenticación inválida."}, status=401)

        order = get_object_or_404(Order, pk=pk, cliente_id=cliente_id)

        if order.status != "PENDIENTE_PAGO":
            return Response(
                {"error": "La orden no está disponible para iniciar el pago."},
                status=409,
            )

        if order.payment_preference_id:
            return Response({
                "orden_id": order.pk,
                "preference_id": order.payment_preference_id,
                "mensaje": "Esta orden ya tiene un checkout creado. No se creó otro.",
            })

        notification_url = os.environ.get("MERCADOPAGO_NOTIFICATION_URL", "")
        try:
            data = crear_checkout(order, notification_url)
        except PaymentError as exc:
            return Response({"error": str(exc.detail)}, status=502)

        order.payment_preference_id = str(data["id"])
        order.save(update_fields=["payment_preference_id", "updated_at"])

        checkout_url = data.get("sandbox_init_point") or data["init_point"]
        return Response({
            "orden_id": order.pk,
            "preference_id": data["id"],
            "checkout_url": checkout_url,
        }, status=201)


def _firma_valida(request, payment_id):
    secret = os.environ.get("MERCADOPAGO_WEBHOOK_SECRET", "")
    signature = request.headers.get("x-signature", "")
    request_id = request.headers.get("x-request-id", "")

    if not secret or not signature or not request_id:
        return False

    parts = {}
    for part in signature.split(","):
        if "=" in part:
            key, value = part.strip().split("=", 1)
            parts[key] = value

    ts = parts.get("ts")
    received_hash = parts.get("v1")
    if not ts or not received_hash:
        return False

    manifest = f"id:{str(payment_id).lower()};request-id:{request_id};ts:{ts};"
    expected = hmac.new(
        secret.encode(), manifest.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, received_hash)


class MercadoPagoWebhookView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        data = request.data
        payment_id = str(
            data.get("data", {}).get("id")
            or request.query_params.get("data.id", "")
        )
        event_type = data.get("type") or request.query_params.get("type", "")

        if event_type != "payment" or not payment_id.isdigit():
            return Response({"received": True}, status=200)

        if not _firma_valida(request, payment_id):
            return Response({"error": "Firma inválida."}, status=401)

        token = os.environ.get("MERCADOPAGO_ACCESS_TOKEN", "")
        if not token:
            return Response({"error": "Pasarela no configurada."}, status=503)

        try:
            response = requests.get(
                "https:" + "/" + "/" + f"api.mercadopago.com/v1/payments/{payment_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            response.raise_for_status()
            payment = response.json()
        except (requests.RequestException, ValueError):
            return Response({"error": "No se pudo verificar el pago."}, status=503)

        order_id = str(payment.get("external_reference", ""))
        if not order_id.isdigit():
            return Response({"error": "Referencia de orden inválida."}, status=400)

        try:
            order = Order.objects.get(pk=int(order_id))
        except Order.DoesNotExist:
            return Response({"error": "Orden no encontrada."}, status=404)

        if payment.get("currency_id") != order.moneda or payment.get("transaction_amount") is None:
            return Response({"error": "Datos del pago no coinciden."}, status=400)

        from decimal import Decimal
        if Decimal(str(payment["transaction_amount"])) != order.total_amount:
            return Response({"error": "El monto del pago no coincide."}, status=400)

        payment_status = str(payment.get("status", "")).lower()
        event_id = f"mp-payment-{payment_id}-{payment_status}"

        try:
            with transaction.atomic():
                event, created = PaymentWebhookEvent.objects.get_or_create(
                    event_id=event_id,
                    defaults={"payment_id": payment_id},
                )
                if not created and event.processed:
                    return Response({"received": True, "duplicate": True}, status=200)

                order = Order.objects.select_for_update().get(pk=order.pk)
                order.payment_id = payment_id
                order.payment_status = payment_status

                if payment_status == "approved":
                    order.status = "CONFIRMACION_PENDIENTE"
                    order.save(update_fields=[
                        "payment_id", "payment_status", "status", "updated_at"
                    ])
                elif payment_status in ("rejected", "cancelled"):
                    if order.status not in ("CONFIRMADA", "CANCELADA", "VENCIDA"):
                        order.status = "RECHAZADA"
                        order.save(update_fields=[
                            "payment_id", "payment_status", "status", "updated_at"
                        ])
                else:
                    order.save(update_fields=[
                        "payment_id", "payment_status", "updated_at"
                    ])
        except IntegrityError:
            return Response({"received": True, "duplicate": True}, status=200)

        if payment_status == "approved":
            try:
                consolidar(f"ORD-{order.pk}")
            except CatalogoError:
                order.status = "REVISION_REQUERIDA"
                order.save(update_fields=["status", "updated_at"])
                return Response({"error": "Pago aprobado; inventario requiere conciliación."}, status=503)

            order.status = "CONFIRMADA"
            order.save(update_fields=["status", "updated_at"])

        elif payment_status in ("rejected", "cancelled"):
            try:
                liberar(
                    f"ORD-{order.pk}",
                    "PAGO_RECHAZADO" if payment_status == "rejected" else "PAGO_CANCELADO",
                )
            except CatalogoError:
                order.status = "REVISION_REQUERIDA"
                order.save(update_fields=["status", "updated_at"])
                return Response({"error": "No se pudo liberar inventario; requiere conciliación."}, status=503)

        PaymentWebhookEvent.objects.filter(event_id=event_id).update(processed=True)
        return Response({"received": True}, status=200)
