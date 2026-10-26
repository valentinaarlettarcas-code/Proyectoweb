from django.urls import path
from .views import CrearOrdenView, DetalleOrdenView
from .payment_views import IniciarPagoView, MercadoPagoWebhookView

urlpatterns = [
    path("ordenes/", CrearOrdenView.as_view(), name="crear-orden"),
    path("ordenes/<int:pk>/", DetalleOrdenView.as_view(), name="detalle-orden"),
    path("ordenes/<int:pk>/pagar/", IniciarPagoView.as_view(), name="iniciar-pago"),
    path("webhooks/mercadopago/", MercadoPagoWebhookView.as_view(), name="webhook-mercadopago"),
]
