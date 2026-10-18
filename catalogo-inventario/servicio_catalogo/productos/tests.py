
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase


class ConsultaProductoTests(SimpleTestCase):

    @patch("productos.views.obtener_bd")
    def test_producto_existente(self, mock_obtener_bd):
        bd = MagicMock()

        bd.productos.find_one.return_value = {
            "id": 1,
            "nombre": "Silla ergonomica X-fire negra",
            "precio": 150000,
            "stock": {"disponible": 10},
            "activo": True
        }

        mock_obtener_bd.return_value = bd

        respuesta = self.client.get("/api/productos/1/")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["precio"], 150000)
        self.assertEqual(respuesta.json()["moneda"], "CLP")
        self.assertEqual(
            respuesta.json()["stock_disponible"], 10
        )

    @patch("productos.views.obtener_bd")
    def test_producto_inexistente(self, mock_obtener_bd):
        bd = MagicMock()

        bd.productos.find_one.return_value = None
        mock_obtener_bd.return_value = bd

        respuesta = self.client.get("/api/productos/999/")

        self.assertEqual(respuesta.status_code, 404)
        self.assertEqual(
            respuesta.json()["codigo"],
            "PRODUCTO_NO_ENCONTRADO"
        )

    @patch("productos.views.obtener_bd")
    def test_catalogo_no_disponible(self, mock_obtener_bd):
        mock_obtener_bd.side_effect = RuntimeError(
            "MongoDB no configurado"
        )

        respuesta = self.client.get("/api/productos/1/")

        self.assertEqual(respuesta.status_code, 503)
        self.assertEqual(
            respuesta.json()["codigo"],
            "CATALOGO_NO_DISPONIBLE"
        )
