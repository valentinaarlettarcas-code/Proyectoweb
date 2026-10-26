from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from .catalogo_client import CatalogoError, reservar, consolidar, liberar


class CatalogoClientTests(SimpleTestCase):
    def setUp(self):
        self.env = patch.dict(
            "os.environ",
            {
                "CATALOGO_API_BASE_URL": "http://catalogo.test",
                "CATALOGO_INTERNAL_TOKEN": "token-prueba",
            },
        )
        self.env.start()
        self.addCleanup(self.env.stop)

    @patch("comercio.catalogo_client.requests.post")
    def test_reservar_envia_contrato_correcto(self, mock_post):
        mock_post.return_value = Mock(
            status_code=201,
            json=lambda: {
                "reserva_id": "ORD-12",
                "orden_id": "12",
                "estado": "RESERVADA",
                "ya_procesada": False,
            },
        )

        resultado = reservar(
            "ORD-12",
            "12",
            [{"producto_id": 5, "quantity": 2}],
        )

        self.assertEqual(resultado["estado"], "RESERVADA")
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "http://catalogo.test/api/reservas/")
        self.assertEqual(
            kwargs["headers"]["Authorization"],
            "Bearer token-prueba",
        )
        self.assertEqual(
            kwargs["json"],
            {
                "reserva_id": "ORD-12",
                "orden_id": "12",
                "productos": [{"producto_id": 5, "cantidad": 2}],
            },
        )

    @patch("comercio.catalogo_client.requests.post")
    def test_consolidar_usa_endpoint_correcto(self, mock_post):
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {"estado": "CONSOLIDADA"},
        )

        consolidar("ORD-12")

        self.assertEqual(
            mock_post.call_args.args[0],
            "http://catalogo.test/api/reservas/ORD-12/consolidar/",
        )

    @patch("comercio.catalogo_client.requests.post")
    def test_liberar_envia_motivo(self, mock_post):
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {"estado": "LIBERADA"},
        )

        liberar("ORD-12", "PAGO_RECHAZADO")

        self.assertEqual(
            mock_post.call_args.kwargs["json"],
            {"motivo": "PAGO_RECHAZADO"},
        )

    @patch("comercio.catalogo_client.requests.post")
    def test_error_503_se_mantiene_como_servicio_no_disponible(
        self, mock_post
    ):
        mock_post.return_value = Mock(
            status_code=503,
            json=lambda: {
                "codigo": "CATALOGO_NO_DISPONIBLE",
                "mensaje": "No disponible",
            },
        )

        with self.assertRaises(CatalogoError) as error:
            consolidar("ORD-12")

        self.assertEqual(error.exception.status_code, 503)

    def test_rechaza_motivo_de_liberacion_invalido(self):
        with self.assertRaises(ValueError):
            liberar("ORD-12", "MOTIVO_INVALIDO")
