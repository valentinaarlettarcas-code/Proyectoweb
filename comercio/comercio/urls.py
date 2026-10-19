from django.urls import path
from .views import CrearOrdenView, DetalleOrdenView

urlpatterns = [
    path("ordenes/", CrearOrdenView.as_view(), name="crear-orden"),
    path("ordenes/<int:pk>/", DetalleOrdenView.as_view(), name="detalle-orden"),
]
