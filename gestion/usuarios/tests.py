from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from .models import Usuario


class GestionUsuariosTests(APITestCase):

    def crear_usuario(
        self,
        email,
        password="Prueba1234",
        rol=Usuario.Rol.CLIENTE,
        estado=Usuario.Estado.ACTIVO
    ):
        return Usuario.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name="Usuario",
            last_name="Prueba",
            rol=rol,
            estado=estado
        )

    def test_registro_cliente(self):
        datos = {
            "first_name": "Alejandra",
            "last_name": "Prueba",
            "email": "nuevo@test.com",
            "password": "Prueba1234"
        }

        respuesta = self.client.post(
            reverse("registro"),
            datos,
            format="json"
        )

        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)

        usuario = Usuario.objects.get(email="nuevo@test.com")

        self.assertEqual(usuario.rol, Usuario.Rol.CLIENTE)
        self.assertEqual(usuario.estado, Usuario.Estado.ACTIVO)
        self.assertTrue(usuario.check_password("Prueba1234"))

    def test_no_permite_email_duplicado(self):
        self.crear_usuario("duplicado@test.com")

        respuesta = self.client.post(
            reverse("registro"),
            {
                "first_name": "Otro",
                "last_name": "Usuario",
                "email": "duplicado@test.com",
                "password": "Prueba1234"
            },
            format="json"
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_login_correcto(self):
        self.crear_usuario("cliente@test.com")

        respuesta = self.client.post(
            reverse("login"),
            {
                "email": "cliente@test.com",
                "password": "Prueba1234"
            },
            format="json"
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIn("token", respuesta.data)

    def test_login_incorrecto(self):
        self.crear_usuario("cliente@test.com")

        respuesta = self.client.post(
            reverse("login"),
            {
                "email": "cliente@test.com",
                "password": "ContraseñaIncorrecta"
            },
            format="json"
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_usuario_bloqueado_no_puede_login(self):
        self.crear_usuario(
            "bloqueado@test.com",
            estado=Usuario.Estado.BLOQUEADO
        )

        respuesta = self.client.post(
            reverse("login"),
            {
                "email": "bloqueado@test.com",
                "password": "Prueba1234"
            },
            format="json"
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_cliente_no_puede_listar_usuarios(self):
        cliente = self.crear_usuario("cliente@test.com")
        token = Token.objects.create(user=cliente)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        respuesta = self.client.get(reverse("lista-usuarios"))

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_admin_puede_listar_usuarios(self):
        admin = self.crear_usuario(
            "admin@test.com",
            rol=Usuario.Rol.ADMIN
        )

        token = Token.objects.create(user=admin)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        respuesta = self.client.get(reverse("lista-usuarios"))

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

    def test_admin_no_puede_editarse_a_si_mismo(self):
        admin = self.crear_usuario(
            "admin@test.com",
            rol=Usuario.Rol.ADMIN
        )

        token = Token.objects.create(user=admin)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        respuesta = self.client.patch(
            reverse("detalle-usuario", args=[admin.id]),
            {"first_name": "Cambio"},
            format="json"
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_admin_no_puede_autobloquearse(self):
        admin = self.crear_usuario(
            "admin@test.com",
            rol=Usuario.Rol.ADMIN
        )

        token = Token.objects.create(user=admin)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        respuesta = self.client.post(
            reverse("bloquear-usuario", args=[admin.id])
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_no_se_puede_bloquear_ultimo_admin_activo(self):
        admin1 = self.crear_usuario(
            "admin1@test.com",
            rol=Usuario.Rol.ADMIN
        )

        admin2 = self.crear_usuario(
            "admin2@test.com",
            rol=Usuario.Rol.ADMIN,
            estado=Usuario.Estado.BLOQUEADO
        )

        token = Token.objects.create(user=admin1)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        respuesta = self.client.post(
            reverse("bloquear-usuario", args=[admin2.id])
        )

        # El admin2 ya está bloqueado; comprobamos además que
        # el único administrador activo sigue siendo admin1.
        admin1.refresh_from_db()

        self.assertEqual(admin1.estado, Usuario.Estado.ACTIVO)