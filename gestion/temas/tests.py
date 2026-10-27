from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from usuarios.models import Usuario

from .models import ConfiguracionSitio


class TemasTests(APITestCase):

    def crear_usuario(
        self,
        email,
        rol=Usuario.Rol.CLIENTE,
        estado=Usuario.Estado.ACTIVO,
    ):
        return Usuario.objects.create_user(
            username=email,
            email=email,
            password="Prueba1234",
            first_name="Usuario",
            last_name="Prueba",
            rol=rol,
            estado=estado,
        )

    def autenticar(self, usuario):
        token, _ = Token.objects.get_or_create(user=usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def tema_activo(self):
        respuesta = self.client.get(reverse("tema-activo"))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        return respuesta.data["identificador"]

    def seleccionar(self, identificador):
        return self.client.post(
            reverse("seleccionar-tema"),
            {"tema": identificador},
            format="json",
        )

    # Lectura publica

    def test_lista_publica_devuelve_cuatro_temas(self):
        respuesta = self.client.get(reverse("lista-temas"))

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        identificadores = [tema["identificador"] for tema in respuesta.data]
        self.assertEqual(
            identificadores, ["tema-1", "tema-2", "tema-3", "tema-4"]
        )

    def test_tema_activo_por_defecto(self):
        self.assertEqual(self.tema_activo(), "tema-1")

    def test_rutas_publicas_no_fallan_con_token_invalido(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token invalido")

        lista = self.client.get(reverse("lista-temas"))
        activo = self.client.get(reverse("tema-activo"))

        self.assertEqual(lista.status_code, status.HTTP_200_OK)
        self.assertEqual(activo.status_code, status.HTTP_200_OK)

    # RF04: seleccion por administrador

    def test_administrador_activo_selecciona_cada_tema(self):
        self.autenticar(self.crear_usuario("admin@test.com", rol=Usuario.Rol.ADMIN))

        for identificador in ["tema-2", "tema-3", "tema-4", "tema-1"]:
            with self.subTest(tema=identificador):
                respuesta = self.seleccionar(identificador)

                self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
                self.assertEqual(respuesta.data["identificador"], identificador)
                self.assertEqual(self.tema_activo(), identificador)

    def test_seleccion_persiste_en_una_sola_configuracion(self):
        self.autenticar(self.crear_usuario("admin@test.com", rol=Usuario.Rol.ADMIN))

        self.seleccionar("tema-3")
        self.seleccionar("tema-2")

        self.assertEqual(ConfiguracionSitio.objects.count(), 1)
        self.assertEqual(
            ConfiguracionSitio.objects.get().tema_activo.identificador, "tema-2"
        )
        self.client.credentials()
        self.assertEqual(self.tema_activo(), "tema-2")

    def test_identificador_inexistente_se_rechaza(self):
        self.autenticar(self.crear_usuario("admin@test.com", rol=Usuario.Rol.ADMIN))
        self.seleccionar("tema-3")

        respuesta = self.seleccionar("tema-99")

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("tema", respuesta.data)
        self.assertEqual(self.tema_activo(), "tema-3")

    def test_campo_ausente_se_rechaza(self):
        self.autenticar(self.crear_usuario("admin@test.com", rol=Usuario.Rol.ADMIN))

        respuesta = self.client.post(
            reverse("seleccionar-tema"), {}, format="json"
        )

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("tema", respuesta.data)
        self.assertEqual(self.tema_activo(), "tema-1")

    # CC-01: solo un administrador activo y autenticado

    def test_visitante_no_puede_seleccionar(self):
        respuesta = self.seleccionar("tema-2")

        self.assertIn(
            respuesta.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )
        self.assertEqual(self.tema_activo(), "tema-1")

    def test_cliente_no_puede_seleccionar(self):
        self.autenticar(self.crear_usuario("cliente@test.com"))

        respuesta = self.seleccionar("tema-2")

        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.tema_activo(), "tema-1")

    def test_administrador_no_activo_no_puede_seleccionar(self):
        for estado in [Usuario.Estado.BLOQUEADO, Usuario.Estado.PENDIENTE]:
            with self.subTest(estado=estado):
                admin = self.crear_usuario(
                    f"admin-{estado}@test.com",
                    rol=Usuario.Rol.ADMIN,
                    estado=estado,
                )
                self.autenticar(admin)

                respuesta = self.seleccionar("tema-2")

                self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)
                self.assertEqual(self.tema_activo(), "tema-1")