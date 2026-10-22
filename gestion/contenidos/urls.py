from django.urls import path

from .views import (
    ContenidoPublicoView,
    DetalleContenidoView,
    ListaCrearContenidoView,
)

urlpatterns = [
    path('', ListaCrearContenidoView.as_view(), name='lista-crear-contenido'),
    path(
        'publico/<slug:pagina>/',
        ContenidoPublicoView.as_view(),
        name='contenido-publico',
    ),
    path('<int:pk>/', DetalleContenidoView.as_view(), name='detalle-contenido'),
]