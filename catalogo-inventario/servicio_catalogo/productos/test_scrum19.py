import json
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient

from .pruebas_gestion import configurar_autenticacion_de_prueba


def generar_imagenes(cantidad):
    """Genera listas validas de URLs y textos alternativos."""
    urls = [f"https://ejemplo.cl/prod/img_{i}.jpg" for i in range(1, cantidad + 1)]
    textos = [f"Vista {i} del producto" for i in range(1, cantidad + 1)]
    return urls, textos


class Scrum19ValidacionesCreacionEdicionTests(SimpleTestCase):
    """Pruebas HTTP faltantes de SCRUM-19 para creacion y edicion de productos."""

    def setUp(self):
        self.cliente = APIClient()
        self.token = "token-pruebas-scrum19"
        self.gestion_http = configurar_autenticacion_de_prueba(self)
        self.cabeceras = {"HTTP_AUTHORIZATION": f"Token {self.token}"}

        urls_base, textos_base = generar_imagenes(4)
        self.payload_base = {
            "id": 101,
            "nombre": "Monitor Gamer 27",
            "descripcion": "Monitor IPS 144Hz para escritorio",
            "precio": 250000,
            "categoria": "Monitores",
            "stock_inicial": 8,
            "imagenes": urls_base,
            "textos_alternativos": textos_base,
        }

    # --- Criterio 2: Precio no positivo (0 o negativo) con 4-6 imagenes ---

    @patch("productos.admin_views.obtener_bd")
    def test_crear_rechaza_precio_negativo_con_imagenes_validas(self, mock_bd):
        urls, textos = generar_imagenes(5)
        datos = {
            **self.payload_base,
            "precio": -5000,
            "imagenes": urls,
            "textos_alternativos": textos,
        }
        respuesta = self.cliente.post(
            "/api/productos/", datos, format="json", **self.cabeceras
        )
        self.assertEqual(respuesta.status_code, 400)
        mock_bd.assert_not_called()

    @patch("productos.admin_views.obtener_bd")
    def test_editar_rechaza_precio_cero_con_imagenes_validas(self, mock_bd):
        urls, textos = generar_imagenes(5)
        datos = {
            "precio": 0,
            "imagenes": urls,
            "textos_alternativos": textos,
        }
        respuesta = self.cliente.patch(
            "/api/admin/productos/101/", datos, format="json", **self.cabeceras
        )
        self.assertEqual(respuesta.status_code, 400)
        mock_bd.assert_not_called()

    # --- Criterio 3: Stock negativo en creacion y edicion con 4-6 imagenes ---

    @patch("productos.admin_views.obtener_bd")
    def test_crear_rechaza_stock_negativo_con_cinco_imagenes(self, mock_bd):
        urls, textos = generar_imagenes(5)
        datos = {
            **self.payload_base,
            "stock_inicial": -3,
            "imagenes": urls,
            "textos_alternativos": textos,
        }
        respuesta = self.cliente.post(
            "/api/productos/", datos, format="json", **self.cabeceras
        )
        self.assertEqual(respuesta.status_code, 400)
        mock_bd.assert_not_called()

    @patch("productos.admin_views.obtener_bd")
    def test_editar_rechaza_stock_negativo_con_imagenes_validas(self, mock_bd):
        urls, textos = generar_imagenes(4)
        datos = {
            "stock": {"disponible": -2, "reservado": 0},
            "imagenes": urls,
            "textos_alternativos": textos,
        }
        respuesta = self.cliente.patch(
            "/api/admin/productos/101/", datos, format="json", **self.cabeceras
        )
        self.assertEqual(respuesta.status_code, 400)
        mock_bd.assert_not_called()

    # --- Criterio 4: Cantidad de imagenes (aceptar 6, rechazar 7 en creacion; 3, 6, 7 en edicion) ---

    @patch("productos.admin_views.obtener_bd")
    def test_crear_acepta_seis_imagenes(self, mock_bd):
        coleccion = mock_bd.return_value.productos
        coleccion.find_one.return_value = None
        urls, textos = generar_imagenes(6)
        datos = {
            **self.payload_base,
            "imagenes": urls,
            "textos_alternativos": textos,
        }
        respuesta = self.cliente.post(
            "/api/productos/", datos, format="json", **self.cabeceras
        )
        self.assertEqual(respuesta.status_code, 201)
        doc_insertado = coleccion.insert_one.call_args.args[0]
        self.assertEqual(len(doc_insertado["imagenes"]), 6)

    @patch("productos.admin_views.obtener_bd")
    def test_crear_rechaza_siete_imagenes(self, mock_bd):
        urls, textos = generar_imagenes(7)
        datos = {
            **self.payload_base,
            "imagenes": urls,
            "textos_alternativos": textos,
        }
        respuesta = self.cliente.post(
            "/api/productos/", datos, format="json", **self.cabeceras
        )
        self.assertEqual(respuesta.status_code, 400)
        mock_bd.assert_not_called()

    @patch("productos.admin_views.obtener_bd")
    def test_editar_acepta_seis_imagenes(self, mock_bd):
        urls, textos = generar_imagenes(6)
        coleccion = mock_bd.return_value.productos
        coleccion.find_one_and_update.return_value = {
            "id": 101,
            "nombre": "Monitor Gamer 27",
            "imagenes": urls,
            "imagenes_accesibles": [
                {"url": u, "texto_alternativo": t} for u, t in zip(urls, textos)
            ],
        }
        respuesta = self.cliente.patch(
            "/api/admin/productos/101/",
            {"imagenes": urls, "textos_alternativos": textos},
            format="json",
            **self.cabeceras,
        )
        self.assertEqual(respuesta.status_code, 200)

    @patch("productos.admin_views.obtener_bd")
    def test_editar_rechaza_tres_y_siete_imagenes(self, mock_bd):
        for cantidad in (3, 7):
            with self.subTest(cantidad=cantidad):
                urls, textos = generar_imagenes(cantidad)
                respuesta = self.cliente.patch(
                    "/api/admin/productos/101/",
                    {"imagenes": urls, "textos_alternativos": textos},
                    format="json",
                    **self.cabeceras,
                )
                self.assertEqual(respuesta.status_code, 400)
        mock_bd.assert_not_called()


class Scrum19CatalogoPublicoYAgotadosTests(SimpleTestCase):
    """Pruebas HTTP faltantes de SCRUM-19 para productos inactivos y agotados."""

    def setUp(self):
        self.cliente = APIClient()
        self.gestion_http = configurar_autenticacion_de_prueba(self)

    # --- Criterio 5: Producto inactivo (activo=False) no visible en catalogo publico ---

    @patch("productos.views.obtener_bd")
    def test_producto_inactivo_no_aparece_en_consulta_publica(self, mock_bd):
        coleccion = mock_bd.return_value.productos
        # Simula que find_one con filtro {"id": 205, "activo": True} no encuentra nada
        coleccion.find_one.return_value = None

        respuesta = self.cliente.get("/api/productos/205/")

        self.assertEqual(respuesta.status_code, 404)
        self.assertEqual(respuesta.json()["codigo"], "PRODUCTO_NO_ENCONTRADO")
        filtro_usado = coleccion.find_one.call_args.args[0]
        self.assertEqual(filtro_usado, {"id": 205, "activo": True})

    # --- Criterio 6: Producto agotado (stock=0) no permite reserva/compra ---

    @patch("productos.reservas_views.obtener_bd")
    @patch.dict("os.environ", {"CATALOGO_INTERNAL_TOKEN": "token-interno-scrum19"})
    def test_producto_agotado_sin_stock_rechaza_reserva(self, mock_bd):
        bd = mock_bd.return_value
        bd.reservas.find_one.return_value = None
        # Simula producto existente con stock disponible en 0
        bd.productos.find_one.return_value = {
            "id": 302,
            "nombre": "Teclado Mecanico Agotado",
            "activo": True,
            "stock": {"disponible": 0, "reservado": 0},
        }
        bd.productos.update_one.return_value.modified_count = 0

        respuesta = self.cliente.post(
            "/api/reservas/",
            data=json.dumps({
                "reserva_id": "RES-AGOTADO-01",
                "orden_id": "ORD-AGOTADO-01",
                "productos": [{"producto_id": 302, "cantidad": 1}],
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer token-interno-scrum19",
        )

        self.assertEqual(respuesta.status_code, 409)
        self.assertEqual(respuesta.json()["codigo"], "CONFLICTO_RESERVA")