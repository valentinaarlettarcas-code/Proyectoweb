from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrdenViewSet, webhook_pago

router = DefaultRouter()
router.register(r"orders", OrdenViewSet, basename="orders")

urlpatterns = [
    path("", include(router.urls)),
    path("payments/webhook/", webhook_pago, name="payments-webhook"),
]
