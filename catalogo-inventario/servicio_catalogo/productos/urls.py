
from django.urls import path

from .views import consultar_producto

urlpatterns = [
    path(
        "productos/<int:producto_id>/",
        consultar_producto,
        name="consultar_producto"
    ),
]
