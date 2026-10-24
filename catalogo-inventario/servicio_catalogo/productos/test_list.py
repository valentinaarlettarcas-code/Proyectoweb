
import os
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient


class ListarProductosAdminHTTPTests(SimpleTestCase):

    def setUp(self):
        self.cliente = APIClient()
        self.ruta = "/api/admin/productos/"
        self.token = "token-pruebas-catalogo"

        self.entorno = patch.dict(
            os.environ,
            {"CATALOGO_ADMIN_TOKEN": self.token},
        )
        self.entorno.start()
        self.addCleanup(self.entorno.stop)

    def obtener_listado(self, token=None):
        encabezado = {
            "HTTP_AUTHORIZATION": "Bearer " + (
                token if token is not None else self.token
            )
        }
        return self.cliente.get(self.ruta, **encabezado)

    @patch("productos.admin_views.obtener_bd")
    def test_listar_productos_activos_e_inactivos(self, mock_bd):
        mock_bd.return_value.productos.find.return_value = [
            {
                "id": 2,
                "nombre": "Producto inactivo",
                "activo": False,
                "precio": 2000,
                "stock": {"disponible": 0, "reservado": 0},
            },
            {
                "id": 1,
                "nombre": "Producto activo",
                "activo": True,
                "precio": 1000,
                "stock": {"disponible": 5, "reservado": 0},
            },
        ]

        respuesta = self.obtener_listado()

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["total"], 2)
        self.assertEqual(
            [producto["id"] for producto in respuesta.data["productos"]],
            [1, 2],
        )
        self.assertTrue(respuesta.data["productos"][0]["activo"])
        self.assertFalse(respuesta.data["productos"][1]["activo"])

    @patch("productos.admin_views.obtener_bd")
    def test_listado_vacio(self, mock_bd):
        mock_bd.return_value.productos.find.return_value = []

        respuesta = self.obtener_listado()

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["total"], 0)
        self.assertEqual(respuesta.data["productos"], [])

    @patch("productos.admin_views.obtener_bd")
    def test_sin_autorizacion(self, mock_bd):
        respuesta = self.cliente.get(self.ruta)

        self.assertEqual(respuesta.status_code, 401)
        mock_bd.assert_not_called()

    @patch("productos.admin_views.obtener_bd")
    def test_token_incorrecto(self, mock_bd):
        respuesta = self.obtener_listado("token-incorrecto")

        self.assertEqual(respuesta.status_code, 401)
        mock_bd.assert_not_called()

    @patch("productos.admin_views.obtener_bd")
    def test_mongodb_no_disponible(self, mock_bd):
        mock_bd.side_effect = RuntimeError("MongoDB no disponible")

        respuesta = self.obtener_listado()

        self.assertEqual(respuesta.status_code, 503)
        self.assertEqual(
            respuesta.data["codigo"],
            "CATALOGO_NO_DISPONIBLE",
        )
