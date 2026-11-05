from django.db import models
from django.core.validators import MinValueValidator

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDIENTE_PAGO', 'Pendiente de Pago'),
        ('CONFIRMACION_PENDIENTE', 'Confirmación Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('RECHAZADA', 'Rechazada'),
        ('CANCELADA', 'Cancelada'),
        ('VENCIDA', 'Vencida'),
        ('REVISION_REQUERIDA', 'Revisión Requerida'),
    ]

    cliente_id = models.IntegerField()
    checkout_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDIENTE_PAGO')
    total_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    moneda = models.CharField(max_length=3, default='CLP')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cliente_id', 'checkout_id'], name='unique_checkout_per_client')
        ]

    def __str__(self):
        return f"Orden {self.id} - Cliente {self.cliente_id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    producto_id = models.CharField(max_length=255)
    
    historical_product_name = models.CharField(max_length=255)
    historical_price = models.DecimalField(max_digits=12, decimal_places=0, validators=[MinValueValidator(1)])
    moneda = models.CharField(max_length=3, default='CLP')
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=0, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.historical_price and self.quantity:
            self.subtotal = self.historical_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.historical_product_name} (Orden #{self.order.id})"