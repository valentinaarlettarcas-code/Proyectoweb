from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Order(models.Model):
    """
    Modelo principal de la Orden de Compra.
    """
    STATUS_CHOICES = [
        ('pending', 'Pendiente de pago'),
        ('paid', 'Pagado'),
        ('processing', 'En preparación'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
    ]

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Pesos chilenos (CLP) sin decimales
    total_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0)

    def __str__(self):
        return f"Orden #{self.id} - {self.user.username} - {self.status}"



class OrderItem(models.Model):
    """
    Modelo de los ítems dentro de la orden.
    Maneja los datos históricos para evitar que cambios en el catálogo afecten compras pasadas.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    
    # Referencia al producto original (SET_NULL por si el producto es eliminado del catálogo en el futuro y no de errores)
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True)

    # --- datos históricos (Snapshots) ---
    historical_product_name = models.CharField(max_length=255, help_text="Nombre del producto tecnológico al comprar")
    historical_price = models.DecimalField(max_digits=12, decimal_places=0, help_text="Precio en CLP al comprar")
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.historical_price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.historical_product_name} (Orden #{self.order.id})" 