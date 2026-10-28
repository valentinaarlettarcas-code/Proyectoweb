"""Cobertura H2: 4 endpoints administrativos x 7 escenarios de seguridad."""
import json
import os
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from django.test import SimpleTestCase
from rest_framework.test import APIClient


URL_GESTION = "http://127.0.0.1:8001/api/usuarios/verificar-token/"
TOKEN = "test-token-gestion-h2"


class SeguridadAdministrativaH2Tests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()
        env = patch.dict(os.environ, {"GESTION_VERIFY_TOKEN_URL": URL_GESTION})
        env.start()
        self.addCleanup(env.stop)

    def operaciones(self):
        """Metodo, ruta, cuerpo JSON, status HTTP esperado para ADMIN."""
        imagenes = [f"https://example.org/img/{i}.jpg" for i in range(4)]
        return (
            ("crear", "POST", "/api/productos/", {
                "id": 401, "nombre": "Producto H2", "descripcion": "Prueba H2",
                "precio": 2000, "categoria": "Pruebas", "stock_inicial": 5,
                "imagenes": imagenes,
            }, 201),
            ("listar", "GET", "/api/admin/productos/", None, 200),
            ("editar", "PATCH", "/api/admin/productos/5/", {
                "nombre": "Producto editado",
            }, 200),
            ("desactivar", "PATCH", "/api/admin/productos/5/desactivar/", {}, 200),
        )

    @staticmethod
    def respuesta_gestion(http, rol="ADMIN", estado="ACTIVO"):
        http.return_value.__enter__.return_value.read.return_value = json.dumps({
            "valido": True,
            "usuario": {"id": 55, "email": "prueba@example.invalid",
                        "rol": rol, "estado": estado},
        }).encode("utf-8")

    @staticmethod
    def preparar_bd(mock_bd):
        coleccion = mock_bd.return_value.productos
        coleccion.find_one.return_value = None
        coleccion.find.return_value = []
        coleccion.find_one_and_update.return_value = {
            "id": 5, "nombre": "Producto editado",
            "activo": False, "stock": {"disponible": 5, "reservado": 0},
        }

    def llamar(self, metodo, ruta, cuerpo, header="Token " + TOKEN):
        encabezados = {}
        if header is not None:
            encabezados["HTTP_AUTHORIZATION"] = header
        if metodo == "GET":
            return self.client.get(ruta, **encabezados)
        if metodo == "POST":
            return self.client.post(ruta, cuerpo, format="json", **encabezados)
        return self.client.patch(ruta, cuerpo, format="json", **encabezados)

    def comprobar(self, escenario, estado_esperado, rol="ADMIN", estado="ACTIVO"):
        for nombre, metodo, ruta, datos, estado_ok in self.operaciones():
            with self.subTest(endpoint=nombre, escenario=escenario):
                with patch("productos.admin_views.obtener_bd") as bd, \
                     patch("productos.autenticacion_gestion.build_opener") as ctor:
                    self.preparar_bd(bd)
                    http = ctor.return_value.open
                    self.respuesta_gestion(http, rol=rol, estado=estado)
                    encabezado = "Token " + TOKEN
                    if escenario == "sin_token":
                        encabezado = None
                    elif escenario == "token_invalido":
                        http.side_effect = HTTPError(
                            URL_GESTION, 401, "Unauthorized", None, None
                        )
                    elif escenario == "gestion_caida":
                        http.side_effect = URLError("connection refused")
                    elif escenario == "bearer_antiguo":
                        encabezado = "Bearer token-temporal"
                    respuesta = self.llamar(metodo, ruta, datos, encabezado)
                    self.assertEqual(
                        respuesta.status_code,
                        estado_ok if estado_esperado == "ok" else estado_esperado,
                    )
                    if estado_esperado != "ok":
                        bd.assert_not_called()

    def test_admin_activo_puede_operar(self):
        self.comprobar("admin", "ok")

    def test_cliente_recibe_403(self):
        self.comprobar("cliente", 403, rol="CLIENTE")

    def test_sin_token_recibe_401(self):
        self.comprobar("sin_token", 401)

    def test_token_falso_recibe_401(self):
        self.comprobar("token_invalido", 401)

    def test_gestion_caida_recibe_503(self):
        self.comprobar("gestion_caida", 503)

    def test_usuario_bloqueado_recibe_403(self):
        self.comprobar("bloqueado", 403, estado="BLOQUEADO")

    def test_token_bearer_antiguo_no_autoriza(self):
        self.comprobar("bearer_antiguo", 401)
