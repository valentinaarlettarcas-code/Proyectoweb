"""Autenticacion de endpoints administrativos contra la API oficial de Gestion.

El token enviado por el cliente se comprueba en Gestion. Nunca se acepta
X-Admin-Id como fuente de identidad, ni se confia en un rol del request.
"""

import json
import os
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import APIException, AuthenticationFailed, PermissionDenied
from rest_framework.permissions import BasePermission


class GestionNoDisponible(APIException):
    status_code = 503
    default_detail = "No fue posible verificar la identidad en Gestion"
    default_code = "gestion_no_disponible"


class _SinRedirecciones(HTTPRedirectHandler):
    """Evita reenviar el token si el servidor responde con un redirect."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


@dataclass(frozen=True)
class UsuarioGestion:
    id: int | str
    email: str
    rol: str
    estado: str

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False


class AutenticacionGestion(BaseAuthentication):
    """GET a verificar-token de Gestion con Authorization: Token <valor>."""

    def authenticate_header(self, request):
        return "Token"

    def authenticate(self, request):
        encabezado = request.headers.get("Authorization", "")
        if not encabezado:
            return None

        esquema, separador, valor = encabezado.partition(" ")
        if esquema.lower() != "token":
            # Los endpoints administrativos no aceptan Bearer interno.
            return None

        token = valor.strip()
        if (
            not separador
            or not token
            or len(token) > 256
            or any(c.isspace() for c in token)
        ):
            raise AuthenticationFailed("Formato de token invalido")

        url = os.environ.get("GESTION_VERIFY_TOKEN_URL", "").strip()
        try:
            partes = urlsplit(url)
        except ValueError:
            raise GestionNoDisponible() from None
        if (
            partes.scheme not in ("http", "https")
            or not partes.hostname
            or partes.username is not None
            or partes.password is not None
            or partes.fragment
        ):
            raise GestionNoDisponible()

        solicitud = Request(
            url,
            method="GET",
            headers={
                "Authorization": f"Token {token}",
                "Accept": "application/json",
                "Cache-Control": "no-store",
            },
        )

        try:
            # Nunca seguir redirecciones que podrian revelar el token.
            with build_opener(_SinRedirecciones()).open(
                solicitud, timeout=3
            ) as respuesta:
                contenido = respuesta.read(65537)
        except HTTPError as error:
            if error.code == 401:
                raise AuthenticationFailed("Token de Gestion invalido") from None
            if error.code == 403:
                raise PermissionDenied("Usuario no autorizado por Gestion") from None
            raise GestionNoDisponible() from None
        except (URLError, OSError, TimeoutError, ValueError):
            raise GestionNoDisponible() from None

        if len(contenido) > 65536:
            raise GestionNoDisponible()
        try:
            cuerpo = json.loads(contenido.decode("utf-8"))
        except (UnicodeError, ValueError, TypeError):
            raise GestionNoDisponible() from None

        if not isinstance(cuerpo, dict):
            raise GestionNoDisponible()
        if cuerpo.get("valido") is not True:
            raise AuthenticationFailed("Token de Gestion invalido")

        datos = cuerpo.get("usuario")
        if not isinstance(datos, dict):
            raise GestionNoDisponible()

        identidad = datos.get("id")
        if (
            (type(identidad) is int and identidad > 0)
            or (type(identidad) is str and 0 < len(identidad.strip()) <= 128)
        ):
            pass
        else:
            raise GestionNoDisponible()

        rol = datos.get("rol")
        estado = datos.get("estado")
        if not isinstance(rol, str) or not isinstance(estado, str):
            raise GestionNoDisponible()
        if estado != "ACTIVO":
            raise PermissionDenied("Usuario de Gestion no activo")

        email = datos.get("email")
        return (UsuarioGestion(
            id=identidad,
            email=email if isinstance(email, str) else "",
            rol=rol,
            estado=estado,
        ), None)


class EsAdminGestion(BasePermission):
    message = "La operacion requiere un administrador activo de Gestion"

    def has_permission(self, request, view):
        return (
            getattr(request.user, "is_authenticated", False)
            and getattr(request.user, "rol", None) == "ADMIN"
            and getattr(request.user, "estado", None) == "ACTIVO"
        )
