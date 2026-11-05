
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient


class ConsultarProductoImagenesTests(SimpleTestCase):

    def setUp(self):
        self.cliente = APIClient()
        self.ruta = "/api/productos/5/"

    @patch("productos.views.obtener_bd")
    def test_consulta_con_imagenes_accesibles(self, mock_bd):
        mock_bd.return_value.productos.find_one.return_value = {
            "id": 5,
            "nombre": "Notebook Lenovo",
            "precio": 450000,
            "activo": True,
            "stock": {"disponible": 10},
            "imagenes": [
                "https://ejemplo.cl/imagen1.jpg"
            ],
            "imagenes_accesibles": [
                {
                    "url": "https://ejemplo.cl/imagen1.jpg",
                    "texto_alternativo": "Vista frontal"
                }
            ]
        }

        respuesta = self.cliente.get(self.ruta)

        self.assertEqual(respuesta.status_code, 200)

        # Contrato original de Comercio.
        self.assertEqual(respuesta.data["id"], 5)
        self.assertEqual(respuesta.data["precio"], 450000)
        self.assertEqual(respuesta.data["moneda"], "CLP")
        self.assertEqual(respuesta.data["stock_disponible"], 10)
        self.assertTrue(respuesta.data["activo"])

        # Campos nuevos.
        self.assertEqual(
            respuesta.data["imagenes"],
            ["https://ejemplo.cl/imagen1.jpg"]
        )
        self.assertEqual(
            respuesta.data["imagenes_accesibles"][0]["texto_alternativo"],
            "Vista frontal"
        )

    @patch("productos.views.obtener_bd")
    def test_producto_antiguo_sin_imagenes_accesibles(self, mock_bd):
        mock_bd.return_value.productos.find_one.return_value = {
            "id": 5,
            "nombre": "Producto antiguo",
            "precio": 20000,
            "activo": True,
            "stock": {"disponible": 3}
        }

        respuesta = self.cliente.get(self.ruta)

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["imagenes"], [])
        self.assertEqual(respuesta.data["imagenes_accesibles"], [])
        self.assertEqual(respuesta.data["stock_disponible"], 3)
