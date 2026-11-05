"""Pruebas de integracion simulada contra verificar-token de Gestion."""
import json
import os
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from django.test import SimpleTestCase
from rest_framework.test import APIClient


class AutenticacionGestionRF19Tests(SimpleTestCase):
    def setUp(self):
        self.cliente = APIClient()
        self.ruta = "/api/admin/productos/5/ajustar-stock/"
        self.token = "a" * 40
        self.url = "http://127.0.0.1:8001/api/usuarios/verificar-token/"
        entorno = patch.dict(
            os.environ, {"GESTION_VERIFY_TOKEN_URL": self.url}
        )
        entorno.start()
        self.addCleanup(entorno.stop)

        parche = patch("productos.autenticacion_gestion.build_opener")
        self.constructor = parche.start()
        self.addCleanup(parche.stop)
        self.http = self.constructor.return_value.open
        self.respuesta_gestion({
            "valido": True,
            "usuario": {
                "id": 42,
                "email": "admin@ejemplo.cl",
                "rol": "ADMIN",
                "estado": "ACTIVO",
            },
        })

    def respuesta_gestion(self, datos):
        self.http.return_value.__enter__.return_value.read.return_value = (
            json.dumps(datos).encode("utf-8")
        )

    def solicitar(self, esquema="Token", con_token=True, extra=None):
        cabeceras = dict(extra or {})
        if con_token:
            cabeceras["HTTP_AUTHORIZATION"] = f"{esquema} {self.token}"
        return self.cliente.post(
            self.ruta,
            {"stock_fisico": 17, "motivo": "Conteo fisico"},
            format="json",
            **cabeceras,
        )

    @patch("productos.stock_admin_views.obtener_bd")
    def test_cliente_no_puede_ajustar(self, mock_bd):
        self.respuesta_gestion({
            "valido": True,
            "usuario": {"id": 8, "rol": "CLIENTE", "estado": "ACTIVO"},
        })
        respuesta = self.solicitar()
        self.assertEqual(respuesta.status_code, 403)
        mock_bd.assert_not_called()

    @patch("productos.stock_admin_views.obtener_bd")
    def test_usuario_bloqueado_rechazado_por_gestion(self, mock_bd):
        self.http.side_effect = HTTPError(
            self.url, 403, "Forbidden", None, None
        )
        self.assertEqual(self.solicitar().status_code, 403)
        mock_bd.assert_not_called()

    @patch("productos.stock_admin_views.obtener_bd")
    def test_estado_no_activo_rechazado_aunque_gestion_responda_200(self, mock_bd):
        self.respuesta_gestion({
            "valido": True,
            "usuario": {"id": 8, "rol": "ADMIN", "estado": "BLOQUEADO"},
        })
        self.assertEqual(self.solicitar().status_code, 403)
        mock_bd.assert_not_called()

    @patch("productos.stock_admin_views.obtener_bd")
    def test_token_declarado_invalido(self, mock_bd):
        self.respuesta_gestion({"valido": False})
        self.assertEqual(self.solicitar().status_code, 401)
        mock_bd.assert_not_called()

    @patch("productos.stock_admin_views.obtener_bd")
    def test_bearer_anterior_ya_no_autoriza(self, mock_bd):
        self.assertEqual(self.solicitar(esquema="Bearer").status_code, 401)
        self.http.assert_not_called()
        mock_bd.assert_not_called()

    @patch("productos.stock_admin_views.obtener_bd")
    def test_sin_token_no_llama_gestion(self, mock_bd):
        self.assertEqual(self.solicitar(con_token=False).status_code, 401)
        self.http.assert_not_called()
        mock_bd.assert_not_called()

    @patch("productos.stock_admin_views.obtener_bd")
    def test_gestion_caida_falla_cerrado(self, mock_bd):
        self.http.side_effect = URLError("connection refused")
        self.assertEqual(self.solicitar().status_code, 503)
        mock_bd.assert_not_called()

    @patch("productos.stock_admin_views.obtener_bd")
    def test_error_500_de_gestion_falla_cerrado(self, mock_bd):
        self.http.side_effect = HTTPError(
            self.url, 500, "Internal Server Error", None, None
        )
        self.assertEqual(self.solicitar().status_code, 503)
        mock_bd.assert_not_called()

    @patch("productos.stock_admin_views.obtener_bd")
    def test_respuesta_gestion_malformada_falla_cerrado(self, mock_bd):
        self.http.return_value.__enter__.return_value.read.return_value = b"no es json"
        self.assertEqual(self.solicitar().status_code, 503)
        mock_bd.assert_not_called()

    @patch("productos.stock_admin_views.obtener_bd")
    def test_identidad_incompleta_falla_cerrado(self, mock_bd):
        self.respuesta_gestion({
            "valido": True,
            "usuario": {"id": None, "rol": "ADMIN", "estado": "ACTIVO"},
        })
        self.assertEqual(self.solicitar().status_code, 503)
        mock_bd.assert_not_called()

    @patch("productos.stock_admin_views.obtener_bd")
    def test_sin_url_configurada_falla_cerrado(self, mock_bd):
        with patch.dict(os.environ, {"GESTION_VERIFY_TOKEN_URL": ""}):
            respuesta = self.solicitar()
        self.assertEqual(respuesta.status_code, 503)
        self.http.assert_not_called()
        mock_bd.assert_not_called()

    @patch("productos.stock_admin_views.obtener_bd")
    def test_reenvia_token_y_no_reenvia_x_admin_id(self, mock_bd):
        self.respuesta_gestion({"valido": False})
        respuesta = self.solicitar(extra={"HTTP_X_ADMIN_ID": "falsificado"})
        self.assertEqual(respuesta.status_code, 401)
        solicitud_http = self.http.call_args.args[0]
        self.assertEqual(
            solicitud_http.get_header("Authorization"), f"Token {self.token}"
        )
        self.assertNotIn("X-admin-id", solicitud_http.headers)
        mock_bd.assert_not_called()
