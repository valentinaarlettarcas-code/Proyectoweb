from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions
from transbank.error.transbank_error import TransbankError
from transbank.webpay.webpay_plus.transaction import Transaction

from .models import IntentoPago, Orden
from .serializers import (
    CrearIntentoPagoSerializer, IntentoPagoSerializer, OrdenSerializer,
)

def _configurar_transbank():
    integration = {
        "TEST": IntegrationType.TEST,
        "LIVE": IntegrationType.LIVE,
    }.get(settings.TBK_ENVIRONMENT, IntegrationType.TEST)

    Transaction.configure(WebpayOptions(
        commerce_code=settings.TBK_COMMERCE_CODE,
        api_key=settings.TBK_API_KEY,
        integration_type=integration,
    ))

def _buy_order(orden):
    return "ORD" + str(orden.id).replace("-", "")[:23]


class OrdenViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /orders/ y GET /orders/{id}/. Ademas action para crear intento."""

    queryset = Orden.objects.all()
    serializer_class = OrdenSerializer
    lookup_field = "id"
    lookup_url_kwarg = "order_id"

    @action(detail=True, methods=["post"], url_path="payment-attempts")
    def crear_intento(self, request, order_id=None):
        orden = get_object_or_404(Orden, id=order_id)

        if orden.estado != Orden.Estado.PENDIENTE_PAGO:
            return Response({"error": {
                "code": "INVALID_STATE_TRANSITION",
                "message": "La orden no admite un nuevo intento de pago.",
            }}, status=status.HTTP_409_CONFLICT)

        serializer = CrearIntentoPagoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return_url = serializer.validated_data["return_url"]

        # Idempotencia: si ya existe intento PENDIENTE, devolverlo.
        previo = orden.intentos_pago.filter(
            estado=IntentoPago.Estado.PENDIENTE
        ).first()
        if previo:
            return Response(
                IntentoPagoSerializer(previo).data, status=status.HTTP_200_OK
            )

        intento = IntentoPago.objects.create(
            orden=orden,
            buy_order=_buy_order(orden),
            session_id=f"ses-{orden.id}"[:61],
            amount=orden.total,
            currency=orden.moneda,
            estado=IntentoPago.Estado.PENDIENTE,
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
            intento.estado = IntentoPago.Estado.REVISION
            intento.save(update_fields=["estado", "actualizado_en"])
            return Response({"error": {
                "code": "PAYMENT_PROVIDER_ERROR",
                "message": "No se pudo crear el intento de pago.",
            }}, status=status.HTTP_502_BAD_GATEWAY)

        intento.token_ws = resp.token
        intento.checkout_url = resp.url
        intento.save(update_fields=["token_ws", "checkout_url", "actualizado_en"])

        return Response(
            IntentoPagoSerializer(intento).data, status=status.HTTP_201_CREATED
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def webhook_pago(request):
    """Webhook declarativo. Webpay Plus no lo usa, queda para H3 u otra pasarela."""
    return Response({"recibido": True}, status=status.HTTP_200_OK)
