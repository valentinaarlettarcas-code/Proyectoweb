import requests
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions
from transbank.error.transbank_error import TransbankError
from transbank.webpay.webpay_plus.transaction import Transaction

from comercio.models import Order, OrderItem
from comercio.catalogo_client import consolidar, liberar
from decimal import Decimal
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .models import IntentoPago
from .serializers import CrearIntentoPagoSerializer, IntentoPagoSerializer


def _verificar_token(request):
    """Usa la autenticación compartida del servicio."""
    from comercio.autenticacion import verificar_token_cliente, ServiceUnavailable

    try:
        return verificar_token_cliente(request), None
    except ServiceUnavailable as exc:
        return None, Response(
            {"error": str(exc)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except Exception as exc:
        return None, Response(
            {"error": str(exc)},
            status=getattr(exc, "status_code", status.HTTP_401_UNAUTHORIZED),
        )


def _buy_order(order):
    return "ORD" + str(order.id).rjust(8, "0")[:23]


class CrearIntentoPagoView(APIView):
    #POST /api/ordenes/<order_id>/payment-attempts/

    permission_classes = []

    def post(self, request, order_id):
        cliente_id, error = _verificar_token(request)
        if error is not None:
            return error

        order = get_object_or_404(Order, pk=order_id)

        # En dev bypass, no validamos propiedad (cliente_id es siempre 1).
        if order.cliente_id != cliente_id:
            return Response(
                {"error": "Orden no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if order.status != "PENDIENTE_PAGO":
            return Response({"error": {
                "code": "INVALID_STATE_TRANSITION",
                "message": "La orden no admite un nuevo intento de pago.",
            }}, status=status.HTTP_409_CONFLICT)

        serializer = CrearIntentoPagoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return_url = serializer.validated_data["return_url"]

        previo = order.intentos_pago.filter(
            status=IntentoPago.Estado.PENDIENTE
        ).first()
        if previo:
            return Response(
                IntentoPagoSerializer(previo).data, status=status.HTTP_200_OK
            )

        intento = IntentoPago.objects.create(
            order=order,
            buy_order=_buy_order(order),
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
                return_url=_url_webpay_return(),
            )
        except Exception as exc:
            import traceback
            traceback.print_exc()
            print(f"ERROR CREANDO INTENTO: {type(exc).__name__}: {exc}")
            intento.status = IntentoPago.Estado.REVISION
            intento.save(update_fields=["status", "updated_at"])
            return Response({"error": {
                "code": "PAYMENT_PROVIDER_ERROR",
                "message": f"No se pudo crear el intento de pago: {type(exc).__name__}: {exc}",
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
    #Webhook declarativo. Webpay Plus no lo usa, queda para H3.
    return Response({"recibido": True}, status=status.HTTP_200_OK)


# ------------------------- DESARROLLO --------------------------------
# RETORNO_WEBPAY_COMERCIO
def _url_webpay_return():
    configured = getattr(settings, "TBK_BACKEND_RETURN_URL", "")
    if configured:
        return configured
    return urlunsplit((
        "http", "127.0.0.1:8000", "/api/payments/return/", "", ""
    ))


def _redirigir_resultado_pago(intento, estado):
    allowed = getattr(settings, "TBK_ALLOWED_RETURN_URLS", [])
    if isinstance(allowed, str):
        allowed = [item.strip() for item in allowed.split(",") if item.strip()]

    destination = intento.return_url
    if destination not in allowed:
        return Response(
            {"error": "La URL de retorno guardada no está permitida."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    parts = urlsplit(destination)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["payment_status"] = estado
    query["order_id"] = str(intento.order_id)
    return redirect(urlunsplit((
        parts.scheme, parts.netloc, parts.path,
        urlencode(query), parts.fragment
    )))


def _marcar_revision(intento):
    intento.status = IntentoPago.Estado.REVISION
    intento.save(update_fields=["status", "updated_at"])
    intento.order.status = "REVISION_REQUERIDA"
    intento.order.save(update_fields=["status", "updated_at"])


@api_view(["POST"])
@permission_classes([AllowAny])
def retorno_webpay(request):
    token_ws = request.data.get("token_ws")

    # Webpay puede volver sin token_ws cuando el usuario cancela.
    if not token_ws:
        buy_order = request.data.get("TBK_ORDEN_COMPRA")
        session_id = request.data.get("TBK_ID_SESION")
        if not buy_order or not session_id:
            return Response(
                {"error": "Faltan los datos de retorno de Webpay."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        intento = IntentoPago.objects.select_related("order").filter(
            buy_order=str(buy_order),
            session_id=str(session_id),
        ).first()
        if intento is None:
            return Response({"error": "Intento de pago no encontrado."}, status=404)

        if intento.status != IntentoPago.Estado.PENDIENTE:
            return _redirigir_resultado_pago(intento, intento.order.status)

        try:
            liberar(f"orden-{intento.order_id}", "PAGO_CANCELADO")
        except Exception:
            _marcar_revision(intento)
            return _redirigir_resultado_pago(intento, "REVISION_REQUERIDA")

        intento.status = IntentoPago.Estado.ANULADO
        intento.save(update_fields=["status", "updated_at"])
        intento.order.status = "CANCELADA"
        intento.order.save(update_fields=["status", "updated_at"])
        return _redirigir_resultado_pago(intento, intento.order.status)

    intento = IntentoPago.objects.select_related("order").filter(
        token_ws=token_ws
    ).first()
    if intento is None:
        return Response({"error": "Intento de pago no encontrado."}, status=404)

    if intento.status != IntentoPago.Estado.PENDIENTE:
        return _redirigir_resultado_pago(intento, intento.order.status)

    try:
        integration = {
            "TEST": IntegrationType.TEST,
            "LIVE": IntegrationType.LIVE,
        }.get(settings.TBK_ENVIRONMENT, IntegrationType.TEST)
        tx = Transaction(WebpayOptions(
            commerce_code=settings.TBK_COMMERCE_CODE,
            api_key=settings.TBK_API_KEY,
            integration_type=integration,
        ))
        resultado = tx.commit(token_ws)
    except Exception:
        _marcar_revision(intento)
        return _redirigir_resultado_pago(intento, "REVISION_REQUERIDA")

    # Verificar orden, sesión e importe antes de aplicar el resultado.
    try:
        valido = (
            str(resultado["buy_order"]) == intento.buy_order
            and str(resultado["session_id"]) == intento.session_id
            and Decimal(str(resultado["amount"])) == intento.amount
        )
        codigo = int(resultado["response_code"])
    except (KeyError, TypeError, ValueError):
        valido = False
        codigo = -1

    if not valido:
        _marcar_revision(intento)
        return _redirigir_resultado_pago(intento, "REVISION_REQUERIDA")

    if codigo == 0:
        intento.status = IntentoPago.Estado.APROBADO
        intento.save(update_fields=["status", "updated_at"])
        intento.order.status = "CONFIRMACION_PENDIENTE"
        intento.order.save(update_fields=["status", "updated_at"])

        try:
            consolidar(f"orden-{intento.order_id}")
        except Exception:
            intento.order.status = "REVISION_REQUERIDA"
            intento.order.save(update_fields=["status", "updated_at"])
            return _redirigir_resultado_pago(intento, "REVISION_REQUERIDA")

        intento.order.status = "CONFIRMADA"
        intento.order.save(update_fields=["status", "updated_at"])
        return _redirigir_resultado_pago(intento, intento.order.status)

    try:
        liberar(f"orden-{intento.order_id}", "PAGO_RECHAZADO")
    except Exception:
        _marcar_revision(intento)
        return _redirigir_resultado_pago(intento, "REVISION_REQUERIDA")

    intento.status = IntentoPago.Estado.RECHAZADO
    intento.save(update_fields=["status", "updated_at"])
    intento.order.status = "RECHAZADA"
    intento.order.save(update_fields=["status", "updated_at"])
    return _redirigir_resultado_pago(intento, intento.order.status)


@api_view(["POST"])
@permission_classes([AllowAny])
def dev_crear_orden_prueba(request):
    #Endpoint de desarrollo. Crea una Order sin Gestion ni Catalogo
    if not settings.DEBUG:
        return Response(
            {"error": "Endpoint no disponible en produccion"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Generar checkout_id unico cada vez (timestamp + random)
    import time
    import random
    checkout_id = f"dev-{int(time.time())}-{random.randint(100, 999)}"

    precio = Decimal("30000")
    cantidad = 1
    total = precio * cantidad

    # Identificador fijo solo para crear órdenes de prueba en DEBUG.
    order = Order.objects.create(
        cliente_id=1,
        checkout_id=checkout_id,
        status="PENDIENTE_PAGO",
        total_amount=total,
        moneda="CLP",
    )
    OrderItem.objects.create(
        order=order,
        producto_id=1,
        historical_product_name="Teclado Mecanico Dev",
        historical_price=precio,
        moneda="CLP",
        quantity=cantidad,
        subtotal=total,
    )

    return Response({
        "id": order.id,
        "checkout_id": order.checkout_id,
        "status": order.status,
        "total_amount": str(order.total_amount),
        "moneda": order.moneda,
    }, status=status.HTTP_201_CREATED)