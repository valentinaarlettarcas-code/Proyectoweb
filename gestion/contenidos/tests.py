from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from usuarios.models import Usuario

from .models import Contenido


class ContenidosTests(APITestCase):

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

    def autenticar_admin(self):
        self.autenticar(self.crear_usuario("admin@test.com", rol=Usuario.Rol.ADMIN))

    def datos(self, **cambios):
        datos = {
            "pagina": "inicio",
            "clave": "bienvenida",
            "tipo": "texto",
            "titulo": "Bienvenido a SetupVerse",
            "cuerpo": "Accesorios tech y gaming para tu setup.",
            "orden": 1,
        }
        datos.update(cambios)
        return datos

    def crear(self, **cambios):
        return self.client.post(
            reverse("lista-crear-contenido"), self.datos(**cambios), format="json"
        )

    def bloque(self, **cambios):
        valores = {
            "pagina": "inicio",
            "clave": "bienvenida",
            "tipo": "texto",
            "titulo": "Bienvenido",
            "cuerpo": "Texto de prueba.",
            "orden": 1,
        }
        valores.update(cambios)
        return Contenido.objects.create(**valores)

    def publico(self, pagina="inicio"):
        return self.client.get(reverse("contenido-publico", args=[pagina]))

    # Lectura publica

    def test_publico_lista_solo_activos_y_ordenados(self):
        self.bloque(clave="segundo", orden=2)
        self.bloque(clave="primero", orden=1)
        self.bloque(clave="oculto", orden=0, activo=False)

        respuesta = self.publico()

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [b["clave"] for b in respuesta.data], ["primero", "segundo"]
        )

    def test_publico_filtra_por_pagina(self):
        self.bloque(clave="a")
        self.bloque(pagina="contacto", clave="direccion")

        respuesta = self.publico("contacto")

        self.assertEqual([b["clave"] for b in respuesta.data], ["direccion"])

    def test_publico_no_expone_campos_internos(self):
        self.bloque()

        bloque = self.publico().data[0]

        for campo in ("id", "activo", "fecha_creacion", "fecha_actualizacion"):
            self.assertNotIn(campo, bloque)

    def test_publico_pagina_inexistente_devuelve_404(self):
        self.assertEqual(self.publico("tienda").status_code, status.HTTP_404_NOT_FOUND)

    def test_publico_no_falla_con_token_invalido(self):
        self.bloque()
        self.client.credentials(HTTP_AUTHORIZATION="Token invalido")

        self.assertEqual(self.publico().status_code, status.HTTP_200_OK)

    def test_cambio_del_admin_se_ve_en_la_siguiente_consulta(self):
        bloque = self.bloque()
        self.autenticar_admin()

        respuesta = self.client.patch(
            reverse("detalle-contenido", args=[bloque.id]),
            {"titulo": "Nuevo titulo"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

        self.client.credentials()
        self.assertEqual(self.publico().data[0]["titulo"], "Nuevo titulo")

    def test_admin_desactiva_bloque_y_deja_de_verse(self):
        bloque = self.bloque()
        self.autenticar_admin()

        respuesta = self.client.patch(
            reverse("detalle-contenido", args=[bloque.id]),
            {"activo": False},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

        self.client.credentials()
        self.assertEqual(len(self.publico().data), 0)

    # Creacion y validaciones

    def test_admin_crea_cada_tipo(self):
        self.autenticar_admin()
        casos = [
            {"clave": "texto-1", "tipo": "texto"},
            {
                "clave": "imagen-1", "tipo": "imagen", "titulo": "", "cuerpo": "",
                "imagen_url": "/img/setup.png",
                "texto_alternativo": "Escritorio gamer",
            },
            {
                "clave": "enlace-1", "tipo": "enlace", "cuerpo": "",
                "titulo": "Ver catalogo",
                "enlace_url": "https://ejemplo.cl/catalogo",
            },
            {
                "clave": "banner-1", "tipo": "banner", "cuerpo": "",
                "titulo": "Oferta", "imagen_url": "/img/banner.png",
                "texto_alternativo": "Banner de oferta",
                "enlace_url": "/catalogo",
            },
        ]
        for caso in casos:
            with self.subTest(tipo=caso["tipo"]):
                respuesta = self.crear(**caso)
                self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Contenido.objects.count(), len(casos))

    def test_validaciones_por_tipo_senalan_el_campo(self):
        self.autenticar_admin()
        casos = [
            ({"cuerpo": "   "}, "cuerpo"),
            ({"cuerpo": "x" * 2001}, "cuerpo"),
            ({"tipo": "imagen", "imagen_url": "", "texto_alternativo": "Logo"}, "imagen_url"),
            ({"tipo": "imagen", "imagen_url": "/img/a.png", "texto_alternativo": ""}, "texto_alternativo"),
            ({"tipo": "enlace", "titulo": "Ver", "enlace_url": ""}, "enlace_url"),
            ({"tipo": "enlace", "titulo": "Ver", "enlace_url": "javascript:alert(1)"}, "enlace_url"),
            ({"tipo": "enlace", "titulo": "Ver", "enlace_url": "//malo.com"}, "enlace_url"),
            ({"tipo": "banner", "titulo": "", "imagen_url": "/img/a.png", "texto_alternativo": "Banner"}, "titulo"),
            ({"pagina": "tienda"}, "pagina"),
            ({"clave": "mi clave"}, "clave"),
            ({"tipo": "video"}, "tipo"),
        ]
        for cambios, campo in casos:
            with self.subTest(campo=campo, cambios=cambios):
                respuesta = self.crear(**cambios)
                self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(campo, respuesta.data)

        self.assertEqual(Contenido.objects.count(), 0)

    def test_clave_repetida_solo_se_rechaza_en_la_misma_pagina(self):
        self.autenticar_admin()

        self.assertEqual(self.crear().status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.crear().status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            self.crear(pagina="contacto").status_code, status.HTTP_201_CREATED
        )
        self.assertEqual(Contenido.objects.count(), 2)

    # Edicion

    def test_edicion_invalida_conserva_los_valores_anteriores(self):
        bloque = self.bloque(cuerpo="Texto original.")
        self.autenticar_admin()

        respuesta = self.client.patch(
            reverse("detalle-contenido", args=[bloque.id]),
            {"cuerpo": ""},
            format="json",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        bloque.refresh_from_db()
        self.assertEqual(bloque.cuerpo, "Texto original.")

    def test_cambiar_el_tipo_se_valida_con_el_tipo_nuevo(self):
        bloque = self.bloque()
        self.autenticar_admin()

        respuesta = self.client.patch(
            reverse("detalle-contenido", args=[bloque.id]),
            {"tipo": "imagen"},
            format="json",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("imagen_url", respuesta.data)
        bloque.refresh_from_db()
        self.assertEqual(bloque.tipo, "texto")

    def test_admin_filtra_la_lista_por_pagina(self):
        self.bloque(clave="a")
        self.bloque(pagina="contacto", clave="direccion")
        self.autenticar_admin()

        respuesta = self.client.get(
            reverse("lista-crear-contenido"), {"pagina": "contacto"}
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual([b["clave"] for b in respuesta.data], ["direccion"])

    def test_detalle_inexistente_devuelve_404(self):
        self.autenticar_admin()

        respuesta = self.client.get(reverse("detalle-contenido", args=[9999]))

        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)

    # Permisos

    def intentar_administrar(self):
        bloque = self.bloque()
        lista = reverse("lista-crear-contenido")
        detalle = reverse("detalle-contenido", args=[bloque.id])
        respuestas = [
            self.client.post(lista, self.datos(clave="otro"), format="json"),
            self.client.patch(detalle, {"titulo": "X"}, format="json"),
            self.client.delete(detalle),
            self.client.get(lista),
        ]
        bloque.refresh_from_db()
        self.assertEqual(bloque.titulo, "Bienvenido")
        self.assertEqual(Contenido.objects.count(), 1)
        return respuestas

    def test_visitante_no_administra_contenidos(self):
        for respuesta in self.intentar_administrar():
            self.assertIn(
                respuesta.status_code,
                (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
            )

    def test_cliente_no_administra_contenidos(self):
        self.autenticar(self.crear_usuario("cliente@test.com"))

        for respuesta in self.intentar_administrar():
            self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_administrador_no_activo_no_administra_contenidos(self):
        for estado in [Usuario.Estado.BLOQUEADO, Usuario.Estado.PENDIENTE]:
            with self.subTest(estado=estado):
                admin = self.crear_usuario(
                    f"admin-{estado}@test.com",
                    rol=Usuario.Rol.ADMIN,
                    estado=estado,
                )
                self.autenticar(admin)

                respuesta = self.client.post(
                    reverse("lista-crear-contenido"),
                    self.datos(clave=f"x-{estado}".lower()),
                    format="json",
                )

                self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)