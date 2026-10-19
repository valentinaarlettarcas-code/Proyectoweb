import uuid

from django.db import models


class Orden(models.Model):
    """Orden de compra. Snapshot historico segun RF-08 y RF-28."""

    class Estado(models.TextChoices):
        PENDIENTE_PAGO = "PENDIENTE_PAGO", "Pendiente de pago"
        CONFIRMACION_PENDIENTE = "CONFIRMACION_PENDIENTE", "Confirmacion pendiente"
        CONFIRMADA = "CONFIRMADA", "Confirmada"
        RECHAZADA = "RECHAZADA", "Rechazada"
        CANCELADA = "CANCELADA", "Cancelada"
        VENCIDA = "VENCIDA", "Vencida"
        REVISION_REQUERIDA = "REVISION_REQUERIDA", "Revision requerida"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente_id = models.CharField(max_length=128, db_index=True)

    # Snapshot de lineas: [{product_id, nombre, precio_unitario, moneda, cantidad}]
    lineas = models.JSONField()

    moneda = models.CharField(max_length=8, default="CLP")
    total = models.DecimalField(max_digits=12, decimal_places=2)

    reserva_id = models.CharField(max_length=128, null=True, blank=True)

    estado = models.CharField(
        max_length=32, choices=Estado.choices, default=Estado.PENDIENTE_PAGO
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    vence_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "pagos_orden"
        ordering = ["-creado_en"]

    def __str__(self):
        return f"Orden {self.id} ({self.estado})"


class IntentoPago(models.Model):
    """Intento de pago en Transbank. buy_order unico = llave idempotente."""

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        APROBADO = "APROBADO", "Aprobado"
        RECHAZADO = "RECHAZADO", "Rechazado"
        ANULADO = "ANULADO", "Anulado"
        REVISION = "REVISION", "Revision"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    orden = models.ForeignKey(
        Orden, on_delete=models.PROTECT, related_name="intentos_pago"
    )

    buy_order = models.CharField(max_length=26, unique=True)
    session_id = models.CharField(max_length=61)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default="CLP")

    token_ws = models.CharField(max_length=128, null=True, blank=True)
    checkout_url = models.URLField(max_length=500, null=True, blank=True)

    estado = models.CharField(
        max_length=16, choices=Estado.choices, default=Estado.PENDIENTE
    )
    return_url = models.URLField(max_length=500)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pagos_intento_pago"
        ordering = ["-creado_en"]
        indexes = [
            models.Index(fields=["orden"], name="idx_intento_orden"),
            models.Index(fields=["estado"], name="idx_intento_estado"),
        ]

    def __str__(self):
        return f"Intento {self.buy_order} ({self.estado})"
