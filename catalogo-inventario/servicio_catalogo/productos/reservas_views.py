
import os
from datetime import datetime, timezone
from hmac import compare_digest

from pymongo.errors import PyMongoError
from rest_framework import serializers, status
from rest_framework.authentication import BaseAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from reservas_stock import reservar_stock
from .mongo import obtener_bd


# Autenticacion interna provisional.
# Se reemplazara al integrar verificar-token de Gestion.
class ServicioInterno:
    is_authenticated = True


class AutenticacionInterna(BaseAuthentication):

    def authenticate(self, request):
        encabezado = request.headers.get("Authorization", "")
        esquema, separador, token = encabezado.partition(" ")

        if esquema.lower() != "bearer" or not separador or not token:
            return None

        esperado = os.environ.get("CATALOGO_INTERNAL_TOKEN")

        if not esperado:
            raise AuthenticationFailed(
                "Autenticacion interna no configurada"
            )

        if not compare_digest(token, esperado):
            raise AuthenticationFailed(
                "Credenciales invalidas"
            )

        return (ServicioInterno(), None)

    def authenticate_header(self, request):
        return "Bearer"


# Validacion de los datos enviados por Comercio.
class LineaReservaSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField(min_value=1)
    cantidad = serializers.IntegerField(min_value=1)


class CrearReservaSerializer(serializers.Serializer):
    reserva_id = serializers.CharField(
        max_length=100,
        allow_blank=False
    )
    orden_id = serializers.CharField(
        max_length=100,
        allow_blank=False
    )
    productos = LineaReservaSerializer(
        many=True,
        allow_empty=False
    )


@api_view(["POST"])
@authentication_classes([AutenticacionInterna])
@permission_classes([IsAuthenticated])
def crear_reserva(request):

    datos = CrearReservaSerializer(data=request.data)

    if not datos.is_valid():
        return Response(
            {
                "codigo": "DATOS_INVALIDOS",
                "mensaje": "Solicitud de reserva invalida",
                "detalles": datos.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    valores = datos.validated_data

    try:
        resultado = reservar_stock(
            obtener_bd(),
            valores["reserva_id"],
            valores["orden_id"],
            valores["productos"]
        )

    except ValueError as error:
        mensaje = str(error)
        texto = mensaje.lower()

        claves_conflicto = (
            "stock insuficiente",
            "producto inactivo",
            "reutilizada",
            "la orden ya tiene",
            "duplicado",
            "duplicada"
        )

        conflicto = any(
            clave in texto for clave in claves_conflicto
        )

        return Response(
            {
                "codigo": (
                    "CONFLICTO_RESERVA"
                    if conflicto else "DATOS_INVALIDOS"
                ),
                "mensaje": mensaje
            },
            status=(
                status.HTTP_409_CONFLICT
                if conflicto
                else status.HTTP_400_BAD_REQUEST
            )
        )

    except (PyMongoError, RuntimeError):
        return Response(
            {
                "codigo": "CATALOGO_NO_DISPONIBLE",
                "mensaje": "No fue posible procesar la reserva"
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    if resultado.get("estado") != "RESERVADA":
        return Response(
            {
                "codigo": "CONFLICTO_RESERVA",
                "mensaje": "La reserva ya no esta en estado RESERVADA"
            },
            status=status.HTTP_409_CONFLICT
        )

    repetida = resultado.get("ya_procesada", False)
    expiracion = resultado.get("fecha_expiracion")

    if isinstance(expiracion, datetime):
        if expiracion.tzinfo is None:
            expiracion = expiracion.replace(tzinfo=timezone.utc)

        expiracion = (
            expiracion.astimezone(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )

    return Response(
        {
            "reserva_id": valores["reserva_id"],
            "orden_id": valores["orden_id"],
            "estado": resultado["estado"],
            "fecha_expiracion": expiracion,
            "ya_procesada": repetida
        },
        status=(
            status.HTTP_200_OK
            if repetida
            else status.HTTP_201_CREATED
        )
    )
