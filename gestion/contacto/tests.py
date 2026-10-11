from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from usuarios.models import Usuario

from .models import MensajeContacto


class ContactoTests(APITestCase):

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

    def datos_validos(self, **cambios):
        datos = {
            "nombre": "Ana Perez",
            "correo": "ana@correo.cl",
            "mensaje": "Hola, quiero consultar por un producto.",
        }
        datos.update(cambios)
        return datos

    def crear_mensaje(self, nombre="Ana Perez"):
        return MensajeContacto.objects.create(
            nombre=nombre,
            correo="ana@correo.cl",
            mensaje="Mensaje de prueba para el listado.",
        )

    def enviar(self, datos):
        return self.client.post(reverse("enviar-mensaje"), datos, format="json")

    # RF05: enviar mensaje de contacto

    def test_visitante_envia_mensaje_valido(self):
        respuesta = self.enviar(self.datos_validos())

        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MensajeContacto.objects.count(), 1)

        mensaje = MensajeContacto.objects.get()
        self.assertEqual(mensaje.nombre, "Ana Perez")
        self.assertEqual(mensaje.correo, "ana@correo.cl")
        self.assertIsNotNone(mensaje.fecha_recepcion)

    def test_datos_invalidos_no_crean_mensaje_y_senalan_campos(self):
        respuesta = self.enviar(
            {"nombre": "A", "correo": "no-es-correo", "mensaje": "corto"}
        )

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nombre", respuesta.data)
        self.assertIn("correo", respuesta.data)
        self.assertIn("mensaje", respuesta.data)
        self.assertEqual(MensajeContacto.objects.count(), 0)

    def test_campos_ausentes_se_rechazan(self):
        respuesta = self.enviar({})

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nombre", respuesta.data)
        self.assertIn("correo", respuesta.data)
        self.assertIn("mensaje", respuesta.data)
        self.assertEqual(MensajeContacto.objects.count(), 0)

    def test_limites_de_longitud(self):
        casos_validos = [
            {"nombre": "Al"},
            {"nombre": "A" * 100},
            {"mensaje": "x" * 10},
            {"mensaje": "x" * 2000},
        ]
        for cambios in casos_validos:
            with self.subTest(valido=cambios):
                respuesta = self.enviar(self.datos_validos(**cambios))
                self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)

        self.assertEqual(MensajeContacto.objects.count(), len(casos_validos))

        casos_invalidos = [
            ({"nombre": "A"}, "nombre"),
            ({"nombre": "A" * 101}, "nombre"),
            ({"mensaje": "x" * 9}, "mensaje"),
            ({"mensaje": "x" * 2001}, "mensaje"),
        ]
        for cambios, campo in casos_invalidos:
            with self.subTest(invalido=campo):
                respuesta = self.enviar(self.datos_validos(**cambios))
                self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(campo, respuesta.data)

        self.assertEqual(MensajeContacto.objects.count(), len(casos_validos))

    def test_envio_no_falla_con_token_invalido(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token invalido")

        respuesta = self.enviar(self.datos_validos())

        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)

    # RF06: consultar mensajes (solo administrador activo)

    def test_visitante_no_accede_al_listado(self):
        self.crear_mensaje()

        respuesta = self.client.get(reverse("lista-mensajes"))

        self.assertIn(
            respuesta.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )
        self.assertNotIn("ana@correo.cl", respuesta.content.decode())

    def test_cliente_no_accede_al_listado(self):
        self.crear_mensaje()
        self.autenticar(self.crear_usuario("cliente@test.com"))

        respuesta = self.client.get(reverse("lista-mensajes"))

        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotIn("ana@correo.cl", respuesta.content.decode())

    def test_administrador_no_activo_no_accede(self):
        self.crear_mensaje()
        estados = [Usuario.Estado.BLOQUEADO, Usuario.Estado.PENDIENTE]
        for estado in estados:
            with self.subTest(estado=estado):
                admin = self.crear_usuario(
                    f"admin-{estado}@test.com",
                    rol=Usuario.Rol.ADMIN,
                    estado=estado,
                )
                self.autenticar(admin)

                respuesta = self.client.get(reverse("lista-mensajes"))

                self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_administrador_activo_ve_listado_ordenado(self):
        self.crear_mensaje(nombre="Primero")
        self.crear_mensaje(nombre="Segundo")
        admin = self.crear_usuario("admin@test.com", rol=Usuario.Rol.ADMIN)
        self.autenticar(admin)

        respuesta = self.client.get(reverse("lista-mensajes"))

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.data), 2)
        self.assertEqual(respuesta.data[0]["nombre"], "Segundo")

    def test_administrador_activo_ve_detalle_completo(self):
        mensaje = self.crear_mensaje()
        admin = self.crear_usuario("admin@test.com", rol=Usuario.Rol.ADMIN)
        self.autenticar(admin)

        respuesta = self.client.get(reverse("detalle-mensaje", args=[mensaje.id]))

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        for campo in ("id", "nombre", "correo", "mensaje", "fecha_recepcion"):
            self.assertIn(campo, respuesta.data)
        self.assertEqual(respuesta.data["correo"], "ana@correo.cl")

    def test_detalle_inexistente_devuelve_404(self):
        self.crear_mensaje()
        admin = self.crear_usuario("admin@test.com", rol=Usuario.Rol.ADMIN)
        self.autenticar(admin)

        respuesta = self.client.get(reverse("detalle-mensaje", args=[9999]))

        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotIn("ana@correo.cl", respuesta.content.decode())

    def test_cliente_y_visitante_no_ven_detalle(self):
        mensaje = self.crear_mensaje()
        url = reverse("detalle-mensaje", args=[mensaje.id])

        respuesta = self.client.get(url)
        self.assertIn(
            respuesta.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

        self.autenticar(self.crear_usuario("cliente@test.com"))
        respuesta = self.client.get(url)
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotIn("ana@correo.cl", respuesta.content.decode())

    def test_administrador_no_puede_modificar_ni_borrar_mensajes(self):
        mensaje = self.crear_mensaje()
        admin = self.crear_usuario("admin@test.com", rol=Usuario.Rol.ADMIN)
        self.autenticar(admin)
        url = reverse("detalle-mensaje", args=[mensaje.id])

        put = self.client.put(url, self.datos_validos(), format="json")
        patch = self.client.patch(url, {"nombre": "Otro"}, format="json")
        delete = self.client.delete(url)

        self.assertEqual(put.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(patch.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(delete.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(MensajeContacto.objects.count(), 1)