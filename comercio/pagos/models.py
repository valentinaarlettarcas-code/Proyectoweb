import uuid

from django.db import models

from comercio.models import Order

class IntentoPago(models.Model):
    #Intento de pago en Transbank Webpay Plus.
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        APROBADO = "APROBADO", "Aprobado"
        RECHAZADO = "RECHAZADO", "Rechazado"
        ANULADO = "ANULADO", "Anulado"
        REVISION = "REVISION", "Revision"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name="intentos_pago"
    )

    buy_order = models.CharField(max_length=26, unique=True)
    session_id = models.CharField(max_length=61)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default="CLP")

    token_ws = models.CharField(max_length=128, null=True, blank=True)
    checkout_url = models.URLField(max_length=500, null=True, blank=True)

    status = models.CharField(
        max_length=16, choices=Estado.choices, default=Estado.PENDIENTE
    )
    return_url = models.URLField(max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pagos_intento_pago"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order"], name="idx_intento_order"),
            models.Index(fields=["status"], name="idx_intento_status"),
        ]

    def __str__(self):
        return f"Intento {self.buy_order} ({self.status})"