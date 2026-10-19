from rest_framework import serializers

from .models import IntentoPago, Orden


class CrearIntentoPagoSerializer(serializers.Serializer):
    """Solo acepta return_url. Monto y moneda vienen de la orden (CC-06)."""

    return_url = serializers.URLField(required=True, max_length=500)

    def validate_return_url(self, value):
        from django.conf import settings
        if value not in settings.TBK_ALLOWED_RETURN_URLS:
            raise serializers.ValidationError("URL de retorno no permitida.")
        return value


class IntentoPagoSerializer(serializers.ModelSerializer):
    payment_attempt_id = serializers.UUIDField(source="id", read_only=True)
    order_id = serializers.UUIDField(source="orden_id", read_only=True)

    class Meta:
        model = IntentoPago
        fields = [
            "payment_attempt_id", "order_id", "estado",
            "checkout_url", "currency", "amount", "buy_order", "creado_en",
        ]
        read_only_fields = fields


class OrdenSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(source="id", read_only=True)

    class Meta:
        model = Orden
        fields = [
            "order_id", "estado", "moneda", "total",
            "lineas", "reserva_id", "creado_en",
        ]
        read_only_fields = fields
