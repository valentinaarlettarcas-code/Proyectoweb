from django.urls import path

from .views import CrearIntentoPagoView, dev_crear_orden_prueba, webhook_pago, retorno_webpay

urlpatterns = [
    path(
        "ordenes/<int:order_id>/payment-attempts/",
        CrearIntentoPagoView.as_view(),
        name="crear-intento-pago",
    ),
    path("payments/webhook/", webhook_pago, name="payments-webhook"),
    path("payments/return/", retorno_webpay, name="payments-return"),
    path("dev/crear-orden-prueba/", dev_crear_orden_prueba, name="dev-crear-orden-prueba"),
]
