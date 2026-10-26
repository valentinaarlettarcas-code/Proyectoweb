
import os
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient

from pymongo.errors import PyMongoError


class DesactivarProductoAdminHTTPTests(SimpleTestCase):

    def setUp(self):
        self.cliente = APIClient()
        self.ruta = "/api/admin/productos/5/desactivar/"
        self.token = "token-pruebas-catalogo"

        entorno = patch.dict(
            os.environ,
            {"CATALOGO_ADMIN_TOKEN": self.token},
        )
        entorno.start()
        self.addCleanup(entorno.stop)

    def desactivar(self, token=None):
        token_usado = self.token if token is None else token

        return self.cliente.patch(
            self.ruta,
            {},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token_usado}",
        )

    @patch("productos.admin_views.obtener_bd")
    def test_desactivacion_exitosa(self, mock_bd):
        producto = {
            "id": 5,
            "nombre": "Notebook",
            "activo": False,
            "stock": {
                "disponible": 7,
                "reservado": 3,
            },
        }

        coleccion = mock_bd.return_value.productos
        coleccion.find_one_and_update.return_value = producto

        respuesta = self.desactivar()

        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(respuesta.data["activo"])

        self.assertEqual(
            respuesta.data["stock"],
            {"disponible": 7, "reservado": 3},
        )

        argumentos = coleccion.find_one_and_update.call_args.args

        self.assertEqual(
            argumentos[0],
            {"id": 5, "activo": True},
        )

        self.assertEqual(
            argumentos[1],
            {"$set": {"activo": False}},
        )

        coleccion.find_one.assert_not_called()

    @patch("productos.admin_views.obtener_bd")
    def test_desactivacion_repetida(self, mock_bd):
        coleccion = mock_bd.return_value.productos

        coleccion.find_one_and_update.return_value = None
        coleccion.find_one.return_value = {
            "id": 5,
            "activo": False,
            "stock": {
                "disponible": 5,
                "reservado": 0,
            },
        }

        respuesta = self.desactivar()

        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(respuesta.data["activo"])
        self.assertIn(
            "ya estaba desactivado",
            respuesta.data["mensaje"],
        )

    @patch("productos.admin_views.obtener_bd")
    def test_producto_inexistente(self, mock_bd):
        coleccion = mock_bd.return_value.productos

        coleccion.find_one_and_update.return_value = None
        coleccion.find_one.return_value = None

        respuesta = self.desactivar()

        self.assertEqual(respuesta.status_code, 404)
        self.assertEqual(
            respuesta.data["codigo"],
            "PRODUCTO_NO_ENCONTRADO",
        )

    @patch("productos.admin_views.obtener_bd")
    def test_sin_autorizacion(self, mock_bd):
        respuesta = self.cliente.patch(
            self.ruta,
            {},
            format="json",
        )

        self.assertEqual(respuesta.status_code, 401)
        mock_bd.assert_not_called()

    @patch("productos.admin_views.obtener_bd")
    def test_token_incorrecto(self, mock_bd):
        respuesta = self.desactivar("token-incorrecto")

        self.assertEqual(respuesta.status_code, 401)
        mock_bd.assert_not_called()

    @patch("productos.admin_views.obtener_bd")
    def test_mongodb_no_disponible(self, mock_bd):
        mock_bd.side_effect = RuntimeError(
            "MongoDB no disponible"
        )

        respuesta = self.desactivar()

        self.assertEqual(respuesta.status_code, 503)
        self.assertEqual(
            respuesta.data["codigo"],
            "CATALOGO_NO_DISPONIBLE",
        )

    @patch("productos.admin_views.obtener_bd")
    def test_error_consulta_producto_inactivo(self, mock_bd):
        coleccion = mock_bd.return_value.productos

        coleccion.find_one_and_update.return_value = None
        coleccion.find_one.side_effect = PyMongoError(
            "Error consultando MongoDB"
        )

        respuesta = self.desactivar()

        self.assertEqual(respuesta.status_code, 503)
