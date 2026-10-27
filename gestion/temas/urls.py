from django.urls import path

from .views import ListaTemasView, SeleccionarTemaView, TemaActivoView

urlpatterns = [
    path('', ListaTemasView.as_view(), name='lista-temas'),
    path('activo/', TemaActivoView.as_view(), name='tema-activo'),
    path('seleccionar/', SeleccionarTemaView.as_view(), name='seleccionar-tema'),
]