
import os
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient


class EditarImagenesProductoTests(SimpleTestCase):

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

        self.imagenes = [
            "https://ejemplo.cl/frontal.jpg",
            "https://ejemplo.cl/trasera.jpg",
            "https://ejemplo.cl/lateral.jpg",
            "https://ejemplo.cl/teclado.jpg",
        ]

        self.textos = [
            "Vista frontal del notebook",
            "Vista trasera del notebook",
            "Vista lateral del notebook",
            "Teclado del notebook",
        ]

    def editar(self, datos):
        return self.cliente.patch(
            self.ruta,
            datos,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )

    @patch("productos.admin_views.obtener_bd")
    def test_actualiza_imagenes_y_textos(self, mock_bd):
        coleccion = mock_bd.return_value.productos

        coleccion.find_one_and_update.return_value = {
            "id": 5,
            "nombre": "Notebook",
            "imagenes": self.imagenes,
            "imagenes_accesibles": [
                {
                    "url": url,
                    "texto_alternativo": texto,
                }
                for url, texto in zip(
                    self.imagenes,
                    self.textos,
                )
            ],
        }

        respuesta = self.editar({
            "imagenes": self.imagenes,
            "textos_alternativos": self.textos,
        })

        self.assertEqual(respuesta.status_code, 200)

        cambios = (
            coleccion.find_one_and_update
            .call_args.args[1]["$set"]
        )

        self.assertEqual(
            cambios["imagenes"],
            self.imagenes,
        )

        self.assertEqual(
            cambios["imagenes_accesibles"][0],
            {
                "url": self.imagenes[0],
                "texto_alternativo": self.textos[0],
            },
        )

        self.assertNotIn("textos_alternativos", cambios)
        self.assertNotIn("stock", cambios)
        self.assertNotIn("activo", cambios)

    @patch("productos.admin_views.obtener_bd")
    def test_rechaza_imagenes_sin_textos(self, mock_bd):
        respuesta = self.editar({
            "imagenes": self.imagenes,
        })

        self.assertEqual(respuesta.status_code, 400)
        mock_bd.assert_not_called()

    @patch("productos.admin_views.obtener_bd")
    def test_rechaza_cantidad_diferente(self, mock_bd):
        respuesta = self.editar({
            "imagenes": self.imagenes,
            "textos_alternativos": self.textos[:-1],
        })

        self.assertEqual(respuesta.status_code, 400)
        mock_bd.assert_not_called()

    @patch("productos.admin_views.obtener_bd")
    def test_editar_nombre_no_modifica_imagenes(self, mock_bd):
        coleccion = mock_bd.return_value.productos

        coleccion.find_one_and_update.return_value = {
            "id": 5,
            "nombre": "Notebook actualizado",
        }

        respuesta = self.editar({
            "nombre": "Notebook actualizado",
        })

        self.assertEqual(respuesta.status_code, 200)

        cambios = (
            coleccion.find_one_and_update
            .call_args.args[1]["$set"]
        )

        self.assertEqual(
            cambios,
            {"nombre": "Notebook actualizado"},
        )
