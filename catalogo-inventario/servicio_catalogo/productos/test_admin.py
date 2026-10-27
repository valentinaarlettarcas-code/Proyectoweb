"""Pruebas HTTP con mocks para el primer endpoint de HU-08."""

import json
import os
from unittest.mock import patch

from django.test import SimpleTestCase
from pymongo.errors import DuplicateKeyError


class CrearProductoHTTPTests(SimpleTestCase):
    def setUp(self):
        entorno = patch.dict(os.environ, {"CATALOGO_ADMIN_TOKEN": "token-admin-de-prueba"})
        entorno.start()
        self.addCleanup(entorno.stop)

        base = patch("productos.admin_views.obtener_bd")
        self.bd = base.start()
        self.addCleanup(base.stop)
        self.bd.return_value.productos.find_one.return_value = None

        self.datos = {
            "id": 40,
            "nombre": "Teclado ergonomico",
            "descripcion": "Teclado para trabajo y estudio",
            "precio": 45000,
            "categoria": "Perifericos",
            "stock_inicial": 10,
            "imagenes": [f"https://example.org/productos/40/{i}.jpg" for i in range(4)],
        }

    def enviar(self, datos=None, token="token-admin-de-prueba", autenticado=True):
        cabeceras = {}
        if autenticado:
            cabeceras["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        return self.client.post(
            "/api/productos/",
            data=json.dumps(self.datos if datos is None else datos),
            content_type="application/json",
            **cabeceras,
        )

    def test_crear_producto_exitoso(self):
        respuesta = self.enviar()
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.json()["moneda"], "CLP")
        documento = self.bd.return_value.productos.insert_one.call_args.args[0]
        self.assertEqual(documento["stock"], {"reservado": 0, "disponible": 10})
        self.assertTrue(documento["activo"])
        self.assertEqual(len(documento["imagenes"]), 4)

    def test_id_duplicado_en_consulta(self):
        self.bd.return_value.productos.find_one.return_value = {"_id": "existente"}
        respuesta = self.enviar()
        self.assertEqual(respuesta.status_code, 409)
        self.assertEqual(respuesta.json()["codigo"], "PRODUCTO_DUPLICADO")
        self.bd.return_value.productos.insert_one.assert_not_called()

    def test_id_duplicado_en_indice(self):
        self.bd.return_value.productos.insert_one.side_effect = DuplicateKeyError("duplicado")
        respuesta = self.enviar()
        self.assertEqual(respuesta.status_code, 409)

    def test_precio_cero(self):
        datos = {**self.datos, "precio": 0}
        respuesta = self.enviar(datos)
        self.assertEqual(respuesta.status_code, 400)
        self.bd.assert_not_called()

    def test_stock_negativo(self):
        datos = {**self.datos, "stock_inicial": -1}
        respuesta = self.enviar(datos)
        self.assertEqual(respuesta.status_code, 400)
        self.bd.assert_not_called()

    def test_tres_imagenes(self):
        datos = {**self.datos, "imagenes": self.datos["imagenes"][:3]}
        respuesta = self.enviar(datos)
        self.assertEqual(respuesta.status_code, 400)
        self.bd.assert_not_called()

    def test_sin_autorizacion(self):
        respuesta = self.enviar(autenticado=False)
        self.assertEqual(respuesta.status_code, 401)
        self.bd.assert_not_called()

    def test_token_incorrecto(self):
        respuesta = self.enviar(token="token-equivocado")
        self.assertEqual(respuesta.status_code, 401)
        self.bd.assert_not_called()

    def test_base_de_datos_no_disponible(self):
        self.bd.side_effect = RuntimeError("MongoDB no configurado")
        respuesta = self.enviar()
        self.assertEqual(respuesta.status_code, 503)
        self.assertEqual(respuesta.json()["codigo"], "CATALOGO_NO_DISPONIBLE")
