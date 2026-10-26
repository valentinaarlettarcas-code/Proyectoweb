import os
from decimal import Decimal
from unittest.mock import Mock, patch

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .catalogo_client import CatalogoError
from .models import Order, OrderItem


@override_settings(
    SECRET_KEY="test-secret-key",
    CATALOGO_API_BASE_URL="http://catalogo.test",
)
class ComercioTests(TestCase):
    def setUp(self):
        os.environ["CATALOGO_API_BASE_URL"] = "http://catalogo.test"
        self.client = APIClient()
        self.auth = {"HTTP_AUTHORIZATION": "Token token-prueba"}
        self.gestion_ok = {
            "valido": True,
            "usuario": {"id": 7, "estado": "ACTIVO"},
        }
        self.catalogo_ok = {
            "nombre": "Producto de prueba",
            "precio": "1000",
            "moneda": "CLP",
            "stock_disponible": 10,
        }
        self.url_crear = "/api/ordenes/"

    @patch(
        "comercio.serializers.reservar",
        return_value={"estado": "RESERVADA", "ya_procesada": False},
    )
    @patch("comercio.views.requests.get")
    def test_crear_orden_con_token_valido(self, mock_get, mock_reservar):
        def respuesta_get(url, **kwargs):
            respuesta = Mock()
            if "/api/usuarios/verificar-token/" in url:
                respuesta.status_code = 200
                respuesta.json.return_value = self.gestion_ok
            elif "/api/productos/1/" in url:
                respuesta.status_code = 200
                respuesta.json.return_value = self.catalogo_ok
            else:
                raise AssertionError(f"URL inesperada: {url}")
            return respuesta

        mock_get.side_effect = respuesta_get

        response = self.client.post(
            self.url_crear,
            {
                "checkout_id": "checkout-prueba-001",
                "items": [{"producto_id": 1, "quantity": 2}],
            },
            format="json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 201, response.data)
        order = Order.objects.get()
        self.assertEqual(order.cliente_id, 7)
        self.assertEqual(order.total_amount, Decimal("2000"))
        self.assertEqual(order.status, "PENDIENTE_PAGO")
        self.assertEqual(OrderItem.objects.filter(order=order).count(), 1)
        mock_reservar.assert_called_once()

    def test_crear_orden_sin_token(self):
        response = self.client.post(
            self.url_crear,
            {
                "checkout_id": "checkout-sin-token",
                "items": [{"producto_id": 1, "quantity": 1}],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    @patch("comercio.views.requests.get")
    def test_rechaza_token_invalido(self, mock_gestion):
        mock_gestion.return_value.status_code = 401

        response = self.client.post(
            self.url_crear,
            {
                "checkout_id": "checkout-token-invalido",
                "items": [{"producto_id": 1, "quantity": 1}],
            },
            format="json",
            **self.auth,
        )
        self.assertEqual(response.status_code, 401)

    @patch("comercio.views.requests.get")
    def test_gestion_no_disponible(self, mock_gestion):
        import requests

        mock_gestion.side_effect = requests.ConnectionError()

        response = self.client.post(
            self.url_crear,
            {
                "checkout_id": "checkout-gestion-caida",
                "items": [{"producto_id": 1, "quantity": 1}],
            },
            format="json",
            **self.auth,
        )
        self.assertEqual(response.status_code, 503)

    @patch("comercio.views.requests.get")
    def test_rechaza_producto_inexistente(self, mock_get):
        def respuesta_get(url, **kwargs):
            respuesta = Mock()
            if "/api/usuarios/verificar-token/" in url:
                respuesta.status_code = 200
                respuesta.json.return_value = self.gestion_ok
            elif "/api/productos/1/" in url:
                respuesta.status_code = 404
            else:
                raise AssertionError(f"URL inesperada: {url}")
            return respuesta

        mock_get.side_effect = respuesta_get

        response = self.client.post(
            self.url_crear,
            {
                "checkout_id": "checkout-producto-inexistente",
                "items": [{"producto_id": 1, "quantity": 1}],
            },
            format="json",
            **self.auth,
        )
        self.assertEqual(response.status_code, 400)

    @patch("comercio.views.requests.get")
    def test_rechaza_productos_repetidos(self, mock_gestion):
        mock_gestion.return_value.status_code = 200
        mock_gestion.return_value.json.return_value = self.gestion_ok

        response = self.client.post(
            self.url_crear,
            {
                "checkout_id": "checkout-duplicados",
                "items": [
                    {"producto_id": 1, "quantity": 1},
                    {"producto_id": 1, "quantity": 2},
                ],
            },
            format="json",
            **self.auth,
        )
        self.assertEqual(response.status_code, 400)

    @patch("comercio.views.requests.get")
    def test_no_permite_consultar_orden_de_otro_cliente(self, mock_gestion):
        mock_gestion.return_value.status_code = 200
        mock_gestion.return_value.json.return_value = self.gestion_ok

        order = Order.objects.create(
            cliente_id=99,
            checkout_id="checkout-otro-cliente",
            total_amount=Decimal("1000"),
        )

        response = self.client.get(
            f"/api/ordenes/{order.pk}/",
            **self.auth,
        )
        self.assertEqual(response.status_code, 404)

    @patch(
        "comercio.serializers.reservar",
        side_effect=CatalogoError("Catálogo no está disponible.", 503),
    )
    @patch("comercio.views.requests.get")
    def test_reserva_fallida_deja_orden_en_revision(
        self, mock_get, mock_reservar
    ):
        def respuesta_get(url, **kwargs):
            respuesta = Mock()
            if "/api/usuarios/verificar-token/" in url:
                respuesta.status_code = 200
                respuesta.json.return_value = self.gestion_ok
            elif "/api/productos/1/" in url:
                respuesta.status_code = 200
                respuesta.json.return_value = self.catalogo_ok
            else:
                raise AssertionError(f"URL inesperada: {url}")
            return respuesta

        mock_get.side_effect = respuesta_get

        response = self.client.post(
            self.url_crear,
            {
                "checkout_id": "checkout-reserva-fallida",
                "items": [{"producto_id": 1, "quantity": 2}],
            },
            format="json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 503)
        order = Order.objects.get(
            checkout_id="checkout-reserva-fallida"
        )
        self.assertEqual(order.status, "REVISION_REQUERIDA")
        mock_reservar.assert_called_once()
