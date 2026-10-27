import logging

import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions
from transbank.error.transbank_error import TransbankError
from transbank.webpay.webpay_plus.transaction import Transaction

from comercio.models import Order
from .models import IntentoPago
from .serializers import CrearIntentoPagoSerializer, IntentoPagoSerializer

logger = logging.getLogger(__name__)


def _verificar_cliente(request):
    """Valida el token con Gestion y exige rol CLIENTE.
    TODO: cuando Jani publique su verificador, reemplazar 
    Retorna (cliente_id, error_response).
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header or not auth_header.lower().startswith("token "):
        return None, Response(
            {"error": "Se requiere Authorization: Token <token>"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    gestion_url = settings.GESTION_VERIFY_TOKEN_URL
    try:
        resp = requests.get(
            gestion_url,
            headers={"Authorization": auth_header, "Accept": "application/json"},
            timeout=5,
        )
    except requests.RequestException:
        logger.warning("Servicio de Gestion no disponible al verificar token")
        return None, Response(
            {"error": "Servicio de Gestion no disponible"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    if resp.status_code != 200:
        return None, Response(
            {"error": "Token invalido o cuenta no activa"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        payload = resp.json()
        usuario = payload.get("usuario", {})
        cliente_id = usuario.get("id")
        rol = str(usuario.get("rol", "")).upper()
        estado = str(usuario.get("estado", "")).lower()
    except (ValueError, AttributeError):
        logger.error("Respuesta invalida de Gestion al verificar token")
        return None, Response(
            {"error": "Respuesta invalida de Gestion"},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    if not payload.get("valido") or not cliente_id:
        return None, Response(
            {"error": "Token invalido"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if estado != "activo":
        return None, Response(
            {"error": "Cuenta no activa"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # RF-10: administradores no pueden pagar.
    if rol != "CLIENTE":
        return None, Response(
            {"error": "Solo los clientes pueden pagar"},
            status=status.HTTP_403_FORBIDDEN,
        )

    return cliente_id, None


def _buy_order(order, intentos_previos):
    """Genera buy_order unico. Incluye contador para evitar colisiones."""
    base = f"ORD{str(order.id).rjust(8, '0')}"
    # Si ya existe, agregar sufijo numerico
    sufijo = intentos_previos
    return f"{base}{sufijo:02d}"[:26]


class CrearIntentoPagoView(APIView):
    """POST /api/ordenes/<order_id>/payment-attempts/"""

    permission_classes = []

    def post(self, request, order_id):
        cliente_id, error = _verificar_cliente(request)
        if error is not None:
            return error

        order = get_object_or_404(Order, pk=order_id)

        # RF-10: cliente solo paga sus propias ordenes.
        if order.cliente_id != cliente_id:
            # 404 para no revelar existencia de la orden (RF-10, seguridad)
            return Response(
                {"error": "Orden no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # RF-27: la orden debe estar pendiente de pago.
        if order.status != "PENDIENTE_PAGO":
            return Response({"error": {
                "code": "INVALID_STATE_TRANSITION",
                "message": "La orden no admite un nuevo intento de pago.",
            }}, status=status.HTTP_409_CONFLICT)

        serializer = CrearIntentoPagoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return_url = serializer.validated_data["return_url"]

        # Idempotencia: si ya existe intento PENDIENTE, devolverlo (doble clic).
        previo = order.intentos_pago.filter(
            status=IntentoPago.Estado.PENDIENTE
        ).first()
        if previo:
            return Response(
                IntentoPagoSerializer(previo).data, status=status.HTTP_200_OK
            )

        # Contar intentos previos para generar buy_order unico.
        intentos_previos = order.intentos_pago.count()

        intento = IntentoPago.objects.create(
            order=order,
            buy_order=_buy_order(order, intentos_previos),
            session_id=f"ses-{order.id}"[:61],
            amount=order.total_amount,
            currency=order.moneda,
            status=IntentoPago.Estado.PENDIENTE,
            return_url=return_url,
        )

        try:
            integration = {
                "TEST": IntegrationType.TEST,
                "LIVE": IntegrationType.LIVE,
            }.get(settings.TBK_ENVIRONMENT, IntegrationType.TEST)

            options = WebpayOptions(
                commerce_code=settings.TBK_COMMERCE_CODE,
                api_key=settings.TBK_API_KEY,
                integration_type=integration,
            )
            tx = Transaction(options)
            resp = tx.create(
                buy_order=intento.buy_order,
                session_id=intento.session_id,
                amount=int(intento.amount),
                return_url=return_url,
            )
        except TransbankError:
            logger.exception(
                "Error de Transbank al crear intento para orden %s", order.id
            )
            intento.status = IntentoPago.Estado.REVISION
            intento.save(update_fields=["status", "updated_at"])
            return Response({"error": {
                "code": "PAYMENT_PROVIDER_ERROR",
                "message": "No se pudo crear el intento de pago.",
            }}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception:
            # logea y no expone detalles al cliente.
            logger.exception(
                "Error inesperado al crear intento para orden %s", order.id
            )
            intento.status = IntentoPago.Estado.REVISION
            intento.save(update_fields=["status", "updated_at"])
            return Response({"error": {
                "code": "PAYMENT_PROVIDER_ERROR",
                "message": "No se pudo crear el intento de pago.",
            }}, status=status.HTTP_502_BAD_GATEWAY)

        intento.token_ws = resp["token"]
        intento.checkout_url = resp["url"]
        intento.save(update_fields=["token_ws", "checkout_url", "updated_at"])

        return Response(
            IntentoPagoSerializer(intento).data, status=status.HTTP_201_CREATED
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def webhook_pago(request):
    return Response(
        {"error": "Webhook no implementado"},
        status=status.HTTP_501_NOT_IMPLEMENTED,
    )