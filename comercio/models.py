from django.db import models

class Order(models.Model):
    """
    Modelo principal de la Orden de Compra.
    """
    # Estados oficiales alineados con la documentación del equipo
    STATUS_CHOICES = [
        ('PENDIENTE_PAGO', 'Pendiente de pago'),
        ('CONFIRMACION_PENDIENTE', 'Confirmación pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('RECHAZADA', 'Rechazada'),
        ('CANCELADA', 'Cancelada'),
        ('VENCIDA', 'Vencida'),
        ('REVISION_REQUERIDA', 'Revisión requerida!!'),
    ]

    # Referencia al usuario sin ForeignKey (Microservicios)
    cliente_id = models.PositiveIntegerField(help_text="ID del cliente en el servicio de Gestión")
    
    # Identificador de checkout para evitar compras duplicadas
    checkout_id = models.CharField(max_length=255, unique=True, help_text="ID único de la operación de checkout")

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDIENTE_PAGO')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Moneda añadida a la orden general
    moneda = models.CharField(max_length=3, default='CLP')
    total_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0)

    def __str__(self):
        return f"Orden #{self.id} - Cliente {self.cliente_id} - {self.status}"


class OrderItem(models.Model):
    """
    Modelo de los ítems dentro de la orden.
    Maneja datos históricos para evitar que cambios en el catálogo afecten compras pasadas.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    
    # Referencia al producto en MongoDB sin ForeignKey
    producto_id = models.CharField(max_length=255, help_text="ID del producto en MongoDB (Catálogo)")

    # --- datos históricos (en Snapshots) ---
    historical_product_name = models.CharField(max_length=255, help_text="Nombre del producto al comprar")
    historical_price = models.DecimalField(max_digits=12, decimal_places=0, help_text="Precio al comprar")
    
    # Moneda y Subtotal físico añadidos
    moneda = models.CharField(max_length=3, default='CLP')
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=12, decimal_places=0, help_text="Subtotal físico al momento de la compra")

    def __str__(self):
        return f"{self.quantity}x {self.historical_product_name} (Orden #{self.order.id})"


