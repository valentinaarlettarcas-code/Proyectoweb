
import os
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient


class ListarProductosAdminHTTPTests(SimpleTestCase):
    """Pruebas del listado administrativo de productos."""

    def setUp(self):
        self.cliente = APIClient()
        self.ruta = "/api/admin/productos/"
        self.token = "token-pruebas-catalogo"

        entorno = patch.dict(
            os.environ,
            {"CATALOGO_ADMIN_TOKEN": self.token},
        )
        entorno.start()
        self.addCleanup(entorno.stop)

    def listar(self):
        """Realiza una solicitud autenticada al listado."""
        return self.cliente.get(
            self.ruta,
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )

    @patch("productos.admin_views.obtener_bd")
    def test_listado_vacio(self, mock_bd):
        """Un catalogo sin productos devuelve una lista vacia."""

        coleccion = mock_bd.return_value.productos
        coleccion.find.return_value = []

        respuesta = self.listar()

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["productos"], [])

    @patch("productos.admin_views.obtener_bd")
    def test_listar_productos_activos_e_inactivos(self, mock_bd):
        """
        El administrador puede visualizar productos activos
        e inactivos, sin depender del orden de MongoDB.
        """

        producto_activo = {
            "id": 1,
            "nombre": "Notebook Lenovo",
            "descripcion": "Notebook para estudiantes",
            "precio": 450000,
            "categoria": "Computacion",
            "stock": {
                "disponible": 10,
                "reservado": 0,
            },
            "imagenes": [
                "https://ejemplo.cl/imagen1.jpg",
                "https://ejemplo.cl/imagen2.jpg",
                "https://ejemplo.cl/imagen3.jpg",
                "https://ejemplo.cl/imagen4.jpg",
            ],
            "activo": True,
        }

        producto_inactivo = {
            "id": 2,
            "nombre": "Mouse inalambrico",
            "descripcion": "Mouse para computador",
            "precio": 15000,
            "categoria": "Accesorios",
            "stock": {
                "disponible": 5,
                "reservado": 0,
            },
            "imagenes": [
                "https://ejemplo.cl/mouse1.jpg",
                "https://ejemplo.cl/mouse2.jpg",
                "https://ejemplo.cl/mouse3.jpg",
                "https://ejemplo.cl/mouse4.jpg",
            ],
            "activo": False,
        }

        coleccion = mock_bd.return_value.productos

        # Simular un resultado sin orden garantizado.
        coleccion.find.return_value = [
            producto_inactivo,
            producto_activo,
        ]

        respuesta = self.listar()

        self.assertEqual(respuesta.status_code, 200)

        productos = respuesta.data["productos"]

        # Deben aparecer ambos productos, sin importar el orden.
        self.assertEqual(len(productos), 2)

        self.assertCountEqual(
            [producto["id"] for producto in productos],
            [1, 2],
        )

        # Consultar el estado utilizando el ID de cada producto.
        productos_por_id = {
            producto["id"]: producto
            for producto in productos
        }

        self.assertTrue(productos_por_id[1]["activo"])
        self.assertFalse(productos_por_id[2]["activo"])

    @patch("productos.admin_views.obtener_bd")
    def test_mongodb_no_disponible(self, mock_bd):
        """El servicio responde 503 cuando MongoDB falla."""

        mock_bd.side_effect = RuntimeError(
            "No se pudo conectar con MongoDB"
        )

        respuesta = self.listar()

        self.assertEqual(respuesta.status_code, 503)

    @patch("productos.admin_views.obtener_bd")
    def test_sin_autorizacion(self, mock_bd):
        """No se permite listar productos sin autenticacion."""

        respuesta = self.cliente.get(self.ruta)

        self.assertEqual(respuesta.status_code, 401)
        mock_bd.assert_not_called()

    @patch("productos.admin_views.obtener_bd")
    def test_token_incorrecto(self, mock_bd):
        """Un token administrativo incorrecto es rechazado."""

        respuesta = self.cliente.get(
            self.ruta,
            HTTP_AUTHORIZATION="Bearer token-incorrecto",
        )

        self.assertEqual(respuesta.status_code, 401)
        mock_bd.assert_not_called()
