"""Pruebas RF-19: usan MongoDB simulado, no prueban transacciones reales."""
import os
from unittest.mock import patch

from django.test import SimpleTestCase
from pymongo.errors import PyMongoError
from rest_framework.test import APIClient


class AjusteStockAdminTests(SimpleTestCase):
    def setUp(self):
        self.cliente = APIClient()
        self.ruta = "/api/admin/productos/5/ajustar-stock/"
        self.entorno = patch.dict(
            os.environ, {"CATALOGO_ADMIN_TOKEN": "token-rf19"}
        )
        self.entorno.start()
        self.addCleanup(self.entorno.stop)

    def solicitud(self, datos=None, usuario="admin01", token="token-rf19"):
        encabezados = {"HTTP_X_ADMIN_ID": usuario}
        if token is not None:
            encabezados["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        return self.cliente.post(
            self.ruta,
            datos if datos is not None else {"stock_fisico": 17, "motivo": "Reposicion"},
            format="json",
            **encabezados,
        )

    def configurar_bd(self, mock_bd, disponible=8, reservado=2):
        bd = mock_bd.return_value
        sesion = bd.client.start_session.return_value.__enter__.return_value
        sesion.with_transaction.side_effect = lambda funcion: funcion(sesion)
        bd.productos.find_one.return_value = {
            "_id": "objeto-mongo-5",
            "id": 5,
            "stock": {"disponible": disponible, "reservado": reservado},
            "activo": True,
        }
        bd.productos.update_one.return_value.matched_count = 1
        return bd, sesion

    @patch("productos.stock_admin_views.obtener_bd")
    def test_ajuste_guarda_auditoria_y_conserva_reservado(self, mock_bd):
        bd, sesion = self.configurar_bd(mock_bd)
        respuesta = self.solicitud()
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["stock_fisico_anterior"], 10)
        self.assertEqual(respuesta.data["stock_fisico_nuevo"], 17)
        self.assertEqual(respuesta.data["stock_disponible_nuevo"], 15)
        actualizacion = bd.productos.update_one.call_args.args[1]
        self.assertEqual(actualizacion, {"$set": {"stock.disponible": 15}})
        self.assertNotIn("stock.reservado", actualizacion["$set"])
        self.assertEqual(
            bd.productos.update_one.call_args.kwargs["session"], sesion
        )
        registro = bd.ajustes_stock.insert_one.call_args.args[0]
        self.assertEqual(registro["usuario_id_reportado"], "admin01")
        self.assertEqual(registro["stock_fisico_anterior"], 10)
        self.assertEqual(registro["stock_fisico_nuevo"], 17)
        self.assertEqual(registro["stock_reservado"], 2)
        self.assertEqual(
            bd.ajustes_stock.insert_one.call_args.kwargs["session"], sesion
        )

    @patch("productos.stock_admin_views.obtener_bd")
    def test_rechaza_stock_inferior_al_reservado(self, mock_bd):
        bd, _ = self.configurar_bd(mock_bd, disponible=8, reservado=4)
        respuesta = self.solicitud({"stock_fisico": 3, "motivo": "Conteo fisico"})
        self.assertEqual(respuesta.status_code, 409)
        bd.productos.update_one.assert_not_called()
        bd.ajustes_stock.insert_one.assert_not_called()

    @patch("productos.stock_admin_views.obtener_bd")
    def test_rechaza_stock_negativo(self, mock_bd):
        respuesta = self.solicitud({"stock_fisico": -1, "motivo": "Conteo fisico"})
        self.assertEqual(respuesta.status_code, 400)
        mock_bd.assert_not_called()

    @patch("productos.stock_admin_views.obtener_bd")
    def test_rechaza_identidad_faltante(self, mock_bd):
        respuesta = self.solicitud(usuario="")
        self.assertEqual(respuesta.status_code, 400)
        mock_bd.assert_not_called()

    @patch("productos.stock_admin_views.obtener_bd")
    def test_rechaza_sin_autenticacion(self, mock_bd):
        respuesta = self.solicitud(token=None)
        self.assertEqual(respuesta.status_code, 401)
        mock_bd.assert_not_called()

    @patch("productos.stock_admin_views.obtener_bd")
    def test_rechaza_token_incorrecto(self, mock_bd):
        respuesta = self.solicitud(token="incorrecto")
        self.assertEqual(respuesta.status_code, 401)
        mock_bd.assert_not_called()

    @patch("productos.stock_admin_views.obtener_bd")
    def test_producto_inexistente(self, mock_bd):
        bd, _ = self.configurar_bd(mock_bd)
        bd.productos.find_one.return_value = None
        respuesta = self.solicitud()
        self.assertEqual(respuesta.status_code, 404)
        bd.productos.update_one.assert_not_called()

    @patch("productos.stock_admin_views.obtener_bd")
    def test_conflicto_de_actualizacion(self, mock_bd):
        bd, _ = self.configurar_bd(mock_bd)
        bd.productos.update_one.return_value.matched_count = 0
        respuesta = self.solicitud()
        self.assertEqual(respuesta.status_code, 409)
        bd.ajustes_stock.insert_one.assert_not_called()

    @patch("productos.stock_admin_views.obtener_bd")
    def test_error_en_auditoria_no_reporta_exito(self, mock_bd):
        bd, sesion = self.configurar_bd(mock_bd)
        bd.ajustes_stock.insert_one.side_effect = PyMongoError("error de escritura")
        respuesta = self.solicitud()
        self.assertEqual(respuesta.status_code, 503)
        sesion.with_transaction.assert_called_once()

    @patch("productos.stock_admin_views.obtener_bd")
    def test_ajuste_sin_cambio_se_rechaza(self, mock_bd):
        bd, _ = self.configurar_bd(mock_bd)
        respuesta = self.solicitud({"stock_fisico": 10, "motivo": "Conteo fisico"})
        self.assertEqual(respuesta.status_code, 400)
        bd.ajustes_stock.insert_one.assert_not_called()
