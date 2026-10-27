"""Tests del modulo de pagos.
Cubren los casos de rechazo que pide el Sprint 3:
- orden ajena (404)
- orden no PENDIENTE_PAGO (409)
- sin token (401)
- administrador rechazado (403)
- error del proveedor Transbank (502)
Para correrlos: python manage.py test pagos
"""
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import TestCase
from rest_framework.test import APIClient

from comercio.models import Order, OrderItem
from pagos.models import IntentoPago


def _mock_gestion(cliente_id=1, rol="CLIENTE", estado="activo", valido=True):
    #Crea un mock de la respuesta de Gestion.
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {
        "valido": valido,
        "usuario": {
            "id": cliente_id,
            "rol": rol,
            "estado": estado,
        },
    }
    return mock


def _crear_orden(cliente_id=1, status="PENDIENTE_PAGO", checkout_id="test-001"):
    #Crea una orden de prueba en la base de datos
    orden = Order.objects.create(
        cliente_id=cliente_id,
        checkout_id=checkout_id,
        status=status,
        total_amount=Decimal("30000"),
        moneda="CLP",
    )
    OrderItem.objects.create(
        order=orden,
        producto_id=1,
        historical_product_name="Teclado Dev",
        historical_price=Decimal("30000"),
        moneda="CLP",
        quantity=1,
        subtotal=Decimal("30000"),
    )
    return orden


class CrearIntentoPagoTests(TestCase):
    #Tests del endpoint POST /api/ordenes/<id>/payment-attempts/.

    def setUp(self):
        self.client = APIClient()
        self.url_return_url = "http://localhost:5173/pago/retorno"
        self.auth_cliente = "Token cliente-token-123"
        self.auth_admin = "Token admin-token-456"

    # --- Caso 1: sin token 401 ---

    @patch("pagos.views.requests.get")
    def test_sin_token_retorna_401(self, mock_get):
        orden = _crear_orden(cliente_id=1)
        response = self.client.post(
            f"/api/ordenes/{orden.pk}/payment-attempts/",
            {"return_url": self.url_return_url},
            format="json",
        )
        self.assertEqual(response.status_code, 401)
        mock_get.assert_not_called()

    # --- Caso 2: orden ajena 404 ---

    @patch("pagos.views.requests.get")
    def test_orden_ajena_retorna_404(self, mock_get):
        # La orden pertenece al cliente 99, pero el token es del cliente 1.
        mock_get.return_value = _mock_gestion(cliente_id=1, rol="CLIENTE")
        orden = _crear_orden(cliente_id=99, checkout_id="otra-orden")

        response = self.client.post(
            f"/api/ordenes/{orden.pk}/payment-attempts/",
            {"return_url": self.url_return_url},
            format="json",
            HTTP_AUTHORIZATION=self.auth_cliente,
        )
        self.assertEqual(response.status_code, 404)

    # --- Caso 3: orden no PENDIENTE_PAGO 409 ---

    @patch("pagos.views.requests.get")
    def test_orden_no_pendiente_retorna_409(self, mock_get):
        mock_get.return_value = _mock_gestion(cliente_id=1, rol="CLIENTE")
        orden = _crear_orden(
            cliente_id=1,
            status="CONFIRMADA",
            checkout_id="orden-confirmada",
        )

        response = self.client.post(
            f"/api/ordenes/{orden.pk}/payment-attempts/",
            {"return_url": self.url_return_url},
            format="json",
            HTTP_AUTHORIZATION=self.auth_cliente,
        )
        self.assertEqual(response.status_code, 409)

    # --- Caso 4: administrador rechazado 403 ---

    @patch("pagos.views.requests.get")
    def test_administrador_rechazado(self, mock_get):
        mock_get.return_value = _mock_gestion(cliente_id=1, rol="ADMIN")
        orden = _crear_orden(cliente_id=1, checkout_id="orden-admin")

        response = self.client.post(
            f"/api/ordenes/{orden.pk}/payment-attempts/",
            {"return_url": self.url_return_url},
            format="json",
            HTTP_AUTHORIZATION=self.auth_admin,
        )
        self.assertEqual(response.status_code, 403)

    # --- Caso 5: error del proveedor Transbank 502 ---

    @patch("pagos.views.requests.get")
    @patch("pagos.views.Transaction")
    def test_error_transbank_retorna_502(self, mock_tx_class, mock_get):
        from transbank.error.transbank_error import TransbankError

        mock_get.return_value = _mock_gestion(cliente_id=1, rol="CLIENTE")

        # Forzar que Transaction.create lance TransbankError
        mock_tx = MagicMock()
        mock_tx.create.side_effect = TransbankError("error", 500)
        mock_tx_class.return_value = mock_tx
        # El constructor Transaction(options) tiene que devolver mock_tx
        mock_tx_class.side_effect = None

        orden = _crear_orden(cliente_id=1, checkout_id="orden-error-tbk")

        response = self.client.post(
            f"/api/ordenes/{orden.pk}/payment-attempts/",
            {"return_url": self.url_return_url},
            format="json",
            HTTP_AUTHORIZATION=self.auth_cliente,
        )
        self.assertEqual(response.status_code, 502)
        # El intento debe quedar en REVISION
        intento = IntentoPago.objects.get(order=orden)
        self.assertEqual(intento.status, IntentoPago.Estado.REVISION)

    # --- idempotencia (doble clic) ---

    @patch("pagos.views.requests.get")
    @patch("pagos.views.Transaction")
    def test_doble_clic_devuelve_mismo_intento(self, mock_tx_class, mock_get):
        mock_get.return_value = _mock_gestion(cliente_id=1, rol="CLIENTE")

        mock_tx = MagicMock()
        mock_tx.create.return_value = {
            "token": "tok-123",
            "url": "https://webpay3gint.transbank.cl/test",
        }
        mock_tx_class.return_value = mock_tx

        orden = _crear_orden(cliente_id=1, checkout_id="orden-doble-clic")

        # Primer POST
        r1 = self.client.post(
            f"/api/ordenes/{orden.pk}/payment-attempts/",
            {"return_url": self.url_return_url},
            format="json",
            HTTP_AUTHORIZATION=self.auth_cliente,
        )
        self.assertEqual(r1.status_code, 201)

        # Segundo POST inmediato (doble clic)
        r2 = self.client.post(
            f"/api/ordenes/{orden.pk}/payment-attempts/",
            {"return_url": self.url_return_url},
            format="json",
            HTTP_AUTHORIZATION=self.auth_cliente,
        )
        self.assertEqual(r2.status_code, 200)
        # Mismo buy_order (es el mismo intento)
        self.assertEqual(r1.data["buy_order"], r2.data["buy_order"])

        # Solo debe existir 1 intento
        self.assertEqual(IntentoPago.objects.filter(order=orden).count(), 1)

#-------------------------------------
# Mensaje en español al terminar los tests
from django.test.runner import DiscoverRunner

class MensajeEspanolRunner(DiscoverRunner):
    def suite_result(self, suite, result):
        n = super().suite_result(suite, result)
        print()
        print("=" * 50)
        print(f"Tests corridos: {result.testsRun}")
        print(f"Fallidos: {len(result.failures)}")
        print(f"Con error: {len(result.errors)}")
        print(f"Omitidos: {len(result.skipped)}")
        print(f"OK: {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
        print("=" * 50)
        return n