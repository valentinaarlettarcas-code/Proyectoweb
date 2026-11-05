from django.urls import path

from .views import DetalleMensajeView, EnviarMensajeView, ListaMensajesView

urlpatterns = [
    path('enviar/', EnviarMensajeView.as_view(), name='enviar-mensaje'),
    path('mensajes/', ListaMensajesView.as_view(), name='lista-mensajes'),
    path('mensajes/<int:pk>/', DetalleMensajeView.as_view(), name='detalle-mensaje'),
]
