import json
import os

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


class CrearReservaHTTPTests(SimpleTestCase):

    def setUp(self):
        # Token ficticio utilizado exclusivamente en pruebas.
        token_patcher = patch.dict(
            os.environ,
            {"CATALOGO_INTERNAL_TOKEN": "token-solo-pruebas"}
        )
        token_patcher.start()
        self.addCleanup(token_patcher.stop)

        # Simular la conexion a MongoDB.
        bd_patcher = patch(
            "productos.reservas_views.obtener_bd"
        )
        self.mock_bd = bd_patcher.start()
        self.addCleanup(bd_patcher.stop)

        # Simular la funcion de reserva existente.
        reserva_patcher = patch(
            "productos.reservas_views.reservar_stock"
        )
        self.mock_reservar = reserva_patcher.start()
        self.addCleanup(reserva_patcher.stop)

        self.datos = {
            "reserva_id": "RES-001",
            "orden_id": "ORD-001",
            "productos": [
                {"producto_id": 1, "cantidad": 2}
            ]
        }

        self.mock_reservar.return_value = {
            "estado": "RESERVADA",
            "ya_procesada": False,
            "fecha_expiracion": None
        }

    def enviar(self, datos=None, autenticado=True,
               token="token-solo-pruebas"):

        encabezados = {}

        if autenticado:
            encabezados["HTTP_AUTHORIZATION"] = (
                f"Bearer {token}"
            )

        return self.client.post(
            "/api/reservas/",
            data=json.dumps(
                self.datos if datos is None else datos
            ),
            content_type="application/json",
            **encabezados
        )

    def test_reserva_nueva(self):
        respuesta = self.enviar()

        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(
            respuesta.json()["estado"], "RESERVADA"
        )
        self.assertFalse(
            respuesta.json()["ya_procesada"]
        )

        self.mock_reservar.assert_called_once_with(
            self.mock_bd.return_value,
            "RES-001",
            "ORD-001",
            [{"producto_id": 1, "cantidad": 2}]
        )

    def test_reserva_repetida(self):
        self.mock_reservar.return_value = {
            "estado": "RESERVADA",
            "ya_procesada": True,
            "fecha_expiracion": None
        }

        respuesta = self.enviar()

        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(
            respuesta.json()["ya_procesada"]
        )

    def test_sin_autenticacion(self):
        respuesta = self.enviar(autenticado=False)

        self.assertEqual(respuesta.status_code, 401)
        self.mock_reservar.assert_not_called()

    def test_token_incorrecto(self):
        respuesta = self.enviar(token="token-incorrecto")

        self.assertEqual(respuesta.status_code, 401)
        self.mock_reservar.assert_not_called()

    def test_cantidad_invalida(self):
        datos = {
            "reserva_id": "RES-002",
            "orden_id": "ORD-002",
            "productos": [
                {"producto_id": 1, "cantidad": 0}
            ]
        }

        respuesta = self.enviar(datos)

        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(
            respuesta.json()["codigo"],
            "DATOS_INVALIDOS"
        )
        self.mock_reservar.assert_not_called()

    def test_stock_insuficiente(self):
        self.mock_reservar.side_effect = ValueError(
            "Stock insuficiente"
        )

        respuesta = self.enviar()

        self.assertEqual(respuesta.status_code, 409)
        self.assertEqual(
            respuesta.json()["codigo"],
            "CONFLICTO_RESERVA"
        )

    def test_mongodb_no_disponible(self):
        self.mock_bd.side_effect = RuntimeError(
            "MongoDB no configurado"
        )

        respuesta = self.enviar()

        self.assertEqual(respuesta.status_code, 503)
        self.assertEqual(
            respuesta.json()["codigo"],
            "CATALOGO_NO_DISPONIBLE"
        )
