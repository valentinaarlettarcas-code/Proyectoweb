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