from django.urls import path
from .views import ListaCrearContenidoView, DetalleContenidoView


urlpatterns = [
    path('', ListaCrearContenidoView.as_view(), name='lista-crear-contenido'),
    path('<int:pk>/', DetalleContenidoView.as_view(), name='detalle-contenido'),
]