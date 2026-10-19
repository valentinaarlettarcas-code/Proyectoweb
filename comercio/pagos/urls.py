from django.urls import path

from .views import CrearIntentoPagoView, dev_crear_orden_prueba, webhook_pago

urlpatterns = [
    path(
        "ordenes/<int:order_id>/payment-attempts/",
        CrearIntentoPagoView.as_view(),
        name="crear-intento-pago",
    ),
    path("payments/webhook/", webhook_pago, name="payments-webhook"),
    path("dev/crear-orden-prueba/", dev_crear_orden_prueba, name="dev-crear-orden-prueba"),
]