
import os
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient


class EditarProductoAdminHTTPTests(SimpleTestCase):

    def setUp(self):
        self.cliente = APIClient()
        self.ruta = "/api/admin/productos/5/"
        self.token = "token-pruebas-catalogo"

        entorno = patch.dict(
            os.environ,
            {"CATALOGO_ADMIN_TOKEN": self.token},
        )
        entorno.start()
        self.addCleanup(entorno.stop)

    def editar(self, datos, token=None):
        token_usado = self.token if token is None else token

        return self.cliente.patch(
            self.ruta,
            datos,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token_usado}",
        )

    @patch("productos.admin_views.obtener_bd")
    def test_edicion_exitosa(self, mock_bd):
        producto = {
            "id": 5,
            "nombre": "Notebook actualizado",
            "precio": 599990,
            "activo": True,
            "stock": {"disponible": 10, "reservado": 2},
        }

        operacion = mock_bd.return_value.productos.find_one_and_update
        operacion.return_value = producto

        respuesta = self.editar({
            "nombre": "Notebook actualizado",
            "precio": 599990,
        })

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            respuesta.data["nombre"],
            "Notebook actualizado",
        )

        argumentos = operacion.call_args.args

        self.assertEqual(argumentos[0], {"id": 5})
        self.assertEqual(
            argumentos[1],
            {
                "$set": {
                    "nombre": "Notebook actualizado",
                    "precio": 599990,
                }
            },
        )
        self.assertNotIn("stock", argumentos[1]["$set"])
        self.assertNotIn("activo", argumentos[1]["$set"])

    @patch("productos.admin_views.obtener_bd")
    def test_editar_producto_inactivo(self, mock_bd):
        mock_bd.return_value.productos.find_one_and_update.return_value = {
            "id": 5,
            "nombre": "Producto corregido",
            "activo": False,
        }

        respuesta = self.editar({
            "nombre": "Producto corregido",
        })

        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(respuesta.data["activo"])

    @patch("productos.admin_views.obtener_bd")
    def test_producto_inexistente(self, mock_bd):
        mock_bd.return_value.productos.find_one_and_update.return_value = None

        respuesta = self.editar({
            "nombre": "Producto nuevo",
        })

        self.assertEqual(respuesta.status_code, 404)

    @patch("productos.admin_views.obtener_bd")
    def test_sin_autorizacion(self, mock_bd):
        respuesta = self.cliente.patch(
            self.ruta,
            {"nombre": "Producto nuevo"},
            format="json",
        )

        self.assertEqual(respuesta.status_code, 401)
        mock_bd.assert_not_called()

    @patch("productos.admin_views.obtener_bd")
    def test_token_incorrecto(self, mock_bd):
        respuesta = self.editar(
            {"nombre": "Producto nuevo"},
            token="token-incorrecto",
        )

        self.assertEqual(respuesta.status_code, 401)
        mock_bd.assert_not_called()

    @patch("productos.admin_views.obtener_bd")
    def test_no_permite_modificar_stock(self, mock_bd):
        respuesta = self.editar({
            "stock": {"disponible": 500, "reservado": 0},
        })

        self.assertEqual(respuesta.status_code, 400)
        mock_bd.assert_not_called()

    @patch("productos.admin_views.obtener_bd")
    def test_no_permite_modificar_id_ni_estado(self, mock_bd):
        respuesta = self.editar({
            "id": 99,
            "activo": False,
        })

        self.assertEqual(respuesta.status_code, 400)
        mock_bd.assert_not_called()

    @patch("productos.admin_views.obtener_bd")
    def test_sin_campos_para_editar(self, mock_bd):
        respuesta = self.editar({})

        self.assertEqual(respuesta.status_code, 400)
        mock_bd.assert_not_called()

    @patch("productos.admin_views.obtener_bd")
    def test_precio_invalido(self, mock_bd):
        respuesta = self.editar({"precio": -100})

        self.assertEqual(respuesta.status_code, 400)
        mock_bd.assert_not_called()

    @patch("productos.admin_views.obtener_bd")
    def test_mongodb_no_disponible(self, mock_bd):
        mock_bd.side_effect = RuntimeError("Sin conexion")

        respuesta = self.editar({
            "nombre": "Producto nuevo",
        })

        self.assertEqual(respuesta.status_code, 503)
        self.assertEqual(
            respuesta.data["codigo"],
            "CATALOGO_NO_DISPONIBLE",
        )
