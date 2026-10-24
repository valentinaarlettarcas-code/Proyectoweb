
from django.urls import path

from .admin_views import (
    crear_producto,
    listar_productos_admin,
    editar_producto_admin,
)

from .views import consultar_producto

from .reservas_views import crear_reserva

from .operaciones_views import (
    consolidar_reserva,
    liberar_reserva,
)


urlpatterns = [
    # Consulta publica utilizada por Comercio.
    path(
        "productos/<int:producto_id>/",
        consultar_producto,
        name="consultar_producto",
    ),

    # Creacion de reservas.
    path(
        "reservas/",
        crear_reserva,
        name="crear_reserva",
    ),

    # Consolidacion de reservas.
    path(
        "reservas/<str:reserva_id>/consolidar/",
        consolidar_reserva,
        name="consolidar_reserva",
    ),

    # Liberacion de reservas.
    path(
        "reservas/<str:reserva_id>/liberar/",
        liberar_reserva,
        name="liberar_reserva",
    ),

    # Creacion administrativa de productos.
    path(
        "productos/",
        crear_producto,
        name="crear_producto",
    ),

    # RF17: Listado administrativo.
    path(
        "admin/productos/",
        listar_productos_admin,
        name="listar_productos_admin",
    ),

    # RF17: Edicion administrativa.
    path(
        "admin/productos/<int:producto_id>/",
        editar_producto_admin,
        name="editar_producto_admin",
    ),
]
