
import os
from unittest.mock import patch
from .pruebas_gestion import configurar_autenticacion_de_prueba, rechazar_token_de_prueba

from django.test import SimpleTestCase
from rest_framework.test import APIClient


class ImagenesAccesiblesTests(SimpleTestCase):

    def setUp(self):
        self.cliente = APIClient()
        self.ruta = "/api/productos/"
        self.token = "token-pruebas-catalogo"

        self.gestion_http = configurar_autenticacion_de_prueba(self)

        self.datos = {
            "id": 51,
            "nombre": "Notebook de prueba",
            "descripcion": "Notebook para uso academico",
            "precio": 450000,
            "categoria": "Computacion",
            "stock_inicial": 10,
            "imagenes": [
                "https://ejemplo.cl/frontal.jpg",
                "https://ejemplo.cl/trasera.jpg",
                "https://ejemplo.cl/lateral.jpg",
                "https://ejemplo.cl/teclado.jpg",
            ],
            "textos_alternativos": [
                "Vista frontal del notebook",
                "Vista trasera del notebook",
                "Vista lateral del notebook",
                "Teclado del notebook",
            ],
        }

    def crear(self):
        return self.cliente.post(
            self.ruta,
            self.datos,
            format="json",
            HTTP_AUTHORIZATION=f"Token {self.token}",
        )

    @patch("productos.admin_views.obtener_bd")
    def test_guarda_imagenes_con_texto_alternativo(self, mock_bd):
        coleccion = mock_bd.return_value.productos
        coleccion.find_one.return_value = None

        respuesta = self.crear()

        self.assertEqual(respuesta.status_code, 201)

        documento = coleccion.insert_one.call_args.args[0]

        self.assertEqual(len(documento["imagenes"]), 4)
        self.assertEqual(len(documento["imagenes_accesibles"]), 4)

        self.assertEqual(
            documento["imagenes_accesibles"][0],
            {
                "url": "https://ejemplo.cl/frontal.jpg",
                "texto_alternativo": "Vista frontal del notebook",
            },
        )

    @patch("productos.admin_views.obtener_bd")
    def test_rechaza_cantidad_distinta_de_textos(self, mock_bd):
        self.datos["textos_alternativos"].append(
            "Imagen adicional sin URL"
        )

        respuesta = self.crear()

        self.assertEqual(respuesta.status_code, 400)
        mock_bd.assert_not_called()

    @patch("productos.admin_views.obtener_bd")
    def test_rechaza_texto_alternativo_vacio(self, mock_bd):
        self.datos["textos_alternativos"][0] = ""

        respuesta = self.crear()

        self.assertEqual(respuesta.status_code, 400)
        mock_bd.assert_not_called()
