
from django.urls import path

from .views import consultar_producto
from .reservas_views import crear_reserva
from .operaciones_views import (
    consolidar_reserva,
    liberar_reserva
)

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
    path(
        "reservas/<str:reserva_id>/consolidar/",
        consolidar_reserva,
        name="consolidar_reserva"
    ),
    path(
        "reservas/<str:reserva_id>/liberar/",
        liberar_reserva,
        name="liberar_reserva"
    ),
]
