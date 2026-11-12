
import io

from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from unittest.mock import patch

Usuario = get_user_model()


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class ImportacionCSVTests(APITestCase):

    def setUp(self):
        self.admin = Usuario.objects.create_user(
            username="admin@test.com",
            email="admin@test.com",
            password="PasswordSegura123!",
            rol=Usuario.Rol.ADMIN,
            estado=Usuario.Estado.ACTIVO,
        )
        self.cliente = Usuario.objects.create_user(
            username="cliente@test.com",
            email="cliente@test.com",
            password="PasswordSegura123!",
            rol=Usuario.Rol.CLIENTE,
            estado=Usuario.Estado.ACTIVO,
        )
        self.url = reverse("importar-usuarios-csv")

    def importar(self, contenido):
        archivo = io.BytesIO(contenido.encode("utf-8"))
        archivo.name = "usuarios.csv"
        return self.client.post(
            self.url,
            {"archivo": archivo},
            format="multipart",
        )

    def test_admin_importa_usuario(self):
        self.client.force_authenticate(user=self.admin)
        respuesta = self.importar(
            "email,nombre,apellido,rol\n"
            "ana@test.com,Ana,Garcia,CLIENTE\n"
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["creados"], 1)
        usuario = Usuario.objects.get(email="ana@test.com")
        self.assertEqual(usuario.estado, Usuario.Estado.PENDIENTE)
        self.assertFalse(usuario.is_active)
        self.assertFalse(usuario.has_usable_password())
        self.assertEqual(len(mail.outbox), 1)

    def test_cliente_no_puede_importar(self):
        self.client.force_authenticate(user=self.cliente)
        respuesta = self.importar(
            "email,nombre,apellido,rol\n"
            "ana@test.com,Ana,Garcia,CLIENTE\n"
        )
        self.assertEqual(respuesta.status_code, 403)

    def test_rechaza_mas_de_200_filas(self):
        self.client.force_authenticate(user=self.admin)
        contenido = "email,nombre,apellido,rol\n"
        for i in range(201):
            contenido += f"usuario{i}@test.com,Ana,Garcia,CLIENTE\n"

        respuesta = self.importar(contenido)
        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(
            Usuario.objects.filter(email__startswith="usuario").count(), 0
        )

    def test_no_duplica_email(self):
        self.client.force_authenticate(user=self.admin)
        respuesta = self.importar(
            "email,nombre,apellido,rol\n"
            "ana@test.com,Ana,Garcia,CLIENTE\n"
            "ana@test.com,Ana,Garcia,CLIENTE\n"
        )
        self.assertEqual(respuesta.data["creados"], 1)
        self.assertEqual(respuesta.data["errores"], 1)

    def test_rechaza_columnas_incorrectas(self):
        self.client.force_authenticate(user=self.admin)
        respuesta = self.importar(
            "email,nombre,rol\n"
            "ana@test.com,Ana,CLIENTE\n"
        )
        self.assertEqual(respuesta.status_code, 400)


    def test_importacion_parcial(self):
        self.client.force_authenticate(user=self.admin)
        respuesta = self.importar(
            "email,nombre,apellido,rol\n"
            "ana@test.com,Ana,Garcia,CLIENTE\n"
            "invalido@test.com,Luis,Lopez,OTRO\n"
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["creados"], 1)
        self.assertEqual(respuesta.data["errores"], 1)

    def test_email_existente(self):
        self.client.force_authenticate(user=self.admin)
        respuesta = self.importar(
            "email,nombre,apellido,rol\n"
            "cliente@test.com,Ana,Garcia,CLIENTE\n"
        )
        self.assertEqual(respuesta.data["creados"], 0)
        self.assertEqual(respuesta.data["errores"], 1)

    def test_respuesta_no_expone_tokens(self):
        self.client.force_authenticate(user=self.admin)
        respuesta = self.importar(
            "email,nombre,apellido,rol\n"
            "ana@test.com,Ana,Garcia,CLIENTE\n"
        )
        contenido = str(respuesta.data).lower()
        self.assertNotIn("token", contenido)
        self.assertNotIn("password", contenido)

    @patch("usuarios.importacion_csv.send_mail")
    def test_fallo_correo_no_crea_usuario(self, enviar):
        enviar.side_effect = OSError("Servidor SMTP no disponible")

        self.client.force_authenticate(user=self.admin)

        respuesta = self.importar(
            "email,nombre,apellido,rol\n"
            "ana@test.com,Ana,Garcia,CLIENTE\n"
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["creados"], 0)
        self.assertEqual(respuesta.data["errores"], 1)
        self.assertFalse(
            Usuario.objects.filter(email="ana@test.com").exists()
        )