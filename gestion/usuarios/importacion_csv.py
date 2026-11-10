
import csv
import hashlib
import io
import secrets

from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.core.mail import BadHeaderError
from smtplib import SMTPException
from django.urls import reverse
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TokenActivacion, Usuario
from .permissions import EsAdministrador
from .serializers import CrearUsuarioAdminSerializer


class ImportarUsuariosCSVView(APIView):
    permission_classes = [EsAdministrador]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        archivo = request.FILES.get("archivo")

        if not archivo:
            return Response(
                {"error": "Debes adjuntar un archivo CSV."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            contenido = archivo.read().decode("utf-8-sig")
            lector = csv.DictReader(
                io.StringIO(contenido),
                strict=True,
            )

            columnas = ["email", "nombre", "apellido", "rol"]

            if lector.fieldnames != columnas:
                return Response(
                    {"error": "Columnas requeridas: email,nombre,apellido,rol"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            filas = list(lector)

        except (UnicodeDecodeError, csv.Error):
            return Response(
                {"error": "CSV inválido o no codificado en UTF-8."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(filas) > 200:
            return Response(
                {"error": "El máximo permitido es 200 filas."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Comprobar la estructura antes de crear usuarios.
        if any(
            None in fila or None in fila.values()
            for fila in filas
        ):
            return Response(
                {"error": "Hay filas con un número incorrecto de columnas."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        resultados = []
        creados = 0
        errores = 0
        emails_procesados = set()

        for numero, fila in enumerate(filas, start=2):
            email = (fila["email"] or "").strip().lower()

            resultado = {
                "fila": numero,
                "email": email,
            }

            if email in emails_procesados:
                resultado.update({
                    "estado": "error",
                    "motivo": "Email repetido en el CSV.",
                })
                errores += 1
                resultados.append(resultado)
                continue

            emails_procesados.add(email)

            datos = {
                "email": email,
                "first_name": fila["nombre"].strip(),
                "last_name": fila["apellido"].strip(),
                "rol": fila["rol"].strip().upper(),
            }

            serializer = CrearUsuarioAdminSerializer(data=datos)

            if not serializer.is_valid():
                resultado.update({
                    "estado": "error",
                    "motivo": serializer.errors,
                })
                errores += 1
                resultados.append(resultado)
                continue

            try:
                with transaction.atomic():
                    usuario = serializer.save()

                    token = secrets.token_urlsafe(32)
                    token_hash = hashlib.sha256(
                        token.encode()
                    ).hexdigest()

                    TokenActivacion.objects.create(
                        usuario=usuario,
                        token_hash=token_hash,
                    )

                    enlace = request.build_absolute_uri(
                        reverse("establecer-password")
                    )

                    send_mail(
                        "Configura tu cuenta",
                        (
                            "Se ha creado una cuenta para ti.\n\n"
                            "Para establecer tu contraseña, utiliza "
                            "este token:\n"
                            f"{token}\n\n"
                            "Envía el token y tu nueva contraseña a:\n"
                            f"{enlace}\n\n"
                            "El token caduca en 24 horas."
                        ),
                        settings.DEFAULT_FROM_EMAIL,
                        [usuario.email],
                        fail_silently=False,
                    )

                resultado.update({
                    "estado": "creado",
                    "motivo": "Pendiente de activación.",
                })
                creados += 1

            except IntegrityError:
                resultado.update({
                    "estado": "error",
                    "motivo": "El usuario ya existe.",
                })
                errores += 1

            except (SMTPException, OSError, BadHeaderError):
                resultado.update({
                    "estado": "error",
                    "motivo": "No se pudo enviar el correo de activación.",
                })
                errores += 1

        return Response(
            {
                "total": len(filas),
                "creados": creados,
                "errores": errores,
                "resultados": resultados,
            },
            status=status.HTTP_200_OK,
        )
