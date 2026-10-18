
from django.urls import path

from .views import consultar_producto
from .reservas_views import crear_reserva

urlpatterns = [
    path(
        "productos/<int:producto_id>/",
        consultar_producto,
        name="consultar_producto"
    ),
    path(
        "reservas/",
        crear_reserva,
        name="crear_reserva"
    ),
]
