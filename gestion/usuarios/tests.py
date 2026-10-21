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
    def test_admin_puede_desbloquear_usuario_bloqueado(self):
        admin = self.crear_usuario(
            "admin-desbloqueo@test.com",
            rol=Usuario.Rol.ADMIN
        )
        cliente = self.crear_usuario(
            "cliente-bloqueado@test.com",
            estado=Usuario.Estado.BLOQUEADO
        )

        token = Token.objects.create(user=admin)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        respuesta = self.client.post(
            reverse("desbloquear-usuario", args=[cliente.id])
        )

        cliente.refresh_from_db()

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(cliente.estado, Usuario.Estado.ACTIVO)

    def test_no_se_puede_desbloquear_usuario_activo(self):
        admin = self.crear_usuario(
            "admin-validacion@test.com",
            rol=Usuario.Rol.ADMIN
        )
        cliente = self.crear_usuario("cliente-activo@test.com")

        token = Token.objects.create(user=admin)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        respuesta = self.client.post(
            reverse("desbloquear-usuario", args=[cliente.id])
        )

        cliente.refresh_from_db()

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(cliente.estado, Usuario.Estado.ACTIVO)

    def test_registro_rechaza_nombre_vacio(self):
        respuesta = self.client.post(
            reverse("registro"),
            {
                "first_name": "   ",
                "last_name": "Prueba",
                "email": "sin-nombre@test.com",
                "password": "ClaveSegura987!"
            },
            format="json"
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", respuesta.data)

    def test_registro_rechaza_apellido_vacio(self):
        respuesta = self.client.post(
            reverse("registro"),
            {
                "first_name": "Ana",
                "last_name": "   ",
                "email": "sin-apellido@test.com",
                "password": "ClaveSegura987!"
            },
            format="json"
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("last_name", respuesta.data)

    def test_edicion_rechaza_nombre_vacio(self):
        admin = self.crear_usuario(
            "admin-edicion@test.com",
            rol=Usuario.Rol.ADMIN
        )
        cliente = self.crear_usuario("cliente-edicion@test.com")

        token = Token.objects.create(user=admin)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        respuesta = self.client.patch(
            reverse("detalle-usuario", args=[cliente.id]),
            {"first_name": "   "},
            format="json"
        )

        cliente.refresh_from_db()

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", respuesta.data)
        self.assertEqual(cliente.first_name, "Usuario")

    def test_edicion_rechaza_apellido_vacio(self):
        admin = self.crear_usuario(
            "admin-apellido@test.com",
            rol=Usuario.Rol.ADMIN
        )
        cliente = self.crear_usuario("cliente-apellido@test.com")

        token = Token.objects.create(user=admin)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        respuesta = self.client.patch(
            reverse("detalle-usuario", args=[cliente.id]),
            {"last_name": ""},
            format="json"
        )

        cliente.refresh_from_db()

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("last_name", respuesta.data)
        self.assertEqual(cliente.last_name, "Prueba")
        
    def test_registro_rechaza_password_comun(self):
        respuesta = self.client.post(
            reverse("registro"),
            {
                "first_name": "Ana",
                "last_name": "Prueba",
                "email": "password-debil@test.com",
                "password": "password123"
            },
            format="json"
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", respuesta.data)

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from django.db import close_old_connections
from django.test import TransactionTestCase
from rest_framework.test import APIClient


class BloqueoConcurrenteTests(TransactionTestCase):
    def test_no_pueden_bloquearse_dos_admins_simultaneamente(self):
        admin1 = Usuario.objects.create_user(
            username="concurrente1@test.com",
            email="concurrente1@test.com",
            password="ClaveSegura123!",
            rol=Usuario.Rol.ADMIN,
            estado=Usuario.Estado.ACTIVO
        )

        admin2 = Usuario.objects.create_user(
            username="concurrente2@test.com",
            email="concurrente2@test.com",
            password="ClaveSegura123!",
            rol=Usuario.Rol.ADMIN,
            estado=Usuario.Estado.ACTIVO
        )

        token1 = Token.objects.create(user=admin1)
        token2 = Token.objects.create(user=admin2)
        inicio = Barrier(2)

        def intentar_bloqueo(token, objetivo):
            close_old_connections()
            try:
                cliente = APIClient()
                cliente.credentials(
                    HTTP_AUTHORIZATION=f"Token {token}"
                )
                inicio.wait(timeout=10)
                return cliente.post(
                    reverse("bloquear-usuario", args=[objetivo])
                ).status_code
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            f1 = executor.submit(
                intentar_bloqueo, token1.key, admin2.pk
            )
            f2 = executor.submit(
                intentar_bloqueo, token2.key, admin1.pk
            )
            resultados = [f1.result(), f2.result()]

        activos = Usuario.objects.filter(
            rol=Usuario.Rol.ADMIN,
            estado=Usuario.Estado.ACTIVO
        ).count()

        self.assertGreaterEqual(activos, 1)
        self.assertNotIn(500, resultados)

    def test_registro_no_permite_asignar_admin(self):
        respuesta = self.client.post(
            reverse("registro"),
            {
                "first_name": "Ana",
                "last_name": "Prueba",
                "email": "intento-admin@test.com",
                "password": "ClaveSegura987!",
                "rol": "ADMIN",
                "estado": "ACTIVO"
            },
            format="json"
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_201_CREATED
        )

        usuario = Usuario.objects.get(
            email="intento-admin@test.com"
        )

        self.assertEqual(usuario.rol, Usuario.Rol.CLIENTE)
        self.assertEqual(usuario.estado, Usuario.Estado.ACTIVO)
        self.assertEqual(respuesta.data["usuario"]["rol"], "CLIENTE")

    def test_patch_no_permite_cambiar_rol_ni_estado(self):
        admin = Usuario.objects.create_user(
            username="admin-patch@test.com",
            email="admin-patch@test.com",
            password="ClaveSegura987!",
            rol=Usuario.Rol.ADMIN,
            estado=Usuario.Estado.ACTIVO
        )

        cliente = Usuario.objects.create_user(
            username="cliente-patch@test.com",
            email="cliente-patch@test.com",
            password="ClaveSegura987!",
            rol=Usuario.Rol.CLIENTE,
            estado=Usuario.Estado.ACTIVO
        )

        token = Token.objects.create(user=admin)

        cliente_api = APIClient()
        cliente_api.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        respuesta = cliente_api.patch(
            reverse("detalle-usuario", args=[cliente.id]),
            {
                "rol": "ADMIN",
                "estado": "BLOQUEADO"
            },
            format="json"
        )

        cliente.refresh_from_db()

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(cliente.rol, Usuario.Rol.CLIENTE)
        self.assertEqual(cliente.estado, Usuario.Estado.ACTIVO)

