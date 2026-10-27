from django.urls import path

from .views import CrearIntentoPagoView, webhook_pago

urlpatterns = [
    path(
        "ordenes/<int:order_id>/payment-attempts/",
        CrearIntentoPagoView.as_view(),
        name="crear-intento-pago",
    ),
    path("payments/webhook/", webhook_pago, name="payments-webhook"),
]