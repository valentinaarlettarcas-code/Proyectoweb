
from django.db import models
from django.core.validators import MinValueValidator

class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDIENTE_PAGO", "Pendiente de pago"),
        ("CONFIRMACION_PENDIENTE", "Confirmación pendiente"),
        ("CONFIRMADA", "Confirmada"),
        ("RECHAZADA", "Rechazada"),
        ("CANCELADA", "Cancelada"),
        ("VENCIDA", "Vencida"),
        ("REVISION_REQUERIDA", "Revisión requerida"),
    ]

    cliente_id = models.PositiveIntegerField(
        help_text="ID del cliente en el servicio de Gestión"
    )
    checkout_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="PENDIENTE_PAGO",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    moneda = models.CharField(max_length=3, default="CLP")
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=0, default=0
    )

    def __str__(self):
        return f"Orden #{self.id} - Cliente {self.cliente_id} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    producto_id = models.CharField(max_length=255)
    
    historical_product_name = models.CharField(max_length=255)
    # Agregamos el MinValueValidator(1) al precio y a la cantidad
    historical_price = models.DecimalField(max_digits=12, decimal_places=0, validators=[MinValueValidator(1)])
    moneda = models.CharField(max_length=3, default='CLP')
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Este campo ahora lo llenaremos automáticamente
    subtotal = models.DecimalField(max_digits=12, decimal_places=0, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Calculamos el subtotal multiplicando precio por cantidad antes de guardar
        if self.historical_price and self.quantity:
            self.subtotal = self.historical_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.historical_product_name} (Orden #{self.order.id})"

