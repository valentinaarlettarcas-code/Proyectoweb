from rest_framework import serializers, status
from operaciones_stock import consolidar_stock, liberar_stock

from pymongo.errors import PyMongoError

from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from operaciones_stock import consolidar_stock

from .mongo import obtener_bd
from .reservas_views import AutenticacionInterna


@api_view(["POST"])
@authentication_classes([AutenticacionInterna])
@permission_classes([IsAuthenticated])
def consolidar_reserva(request, reserva_id):
    """
    Consolida una reserva previamente autorizada.

    La confirmacion del pago debe realizarse
    desde el servicio de Comercio.
    """

    try:
        bd = obtener_bd()

    except RuntimeError:
        return Response(
            {
                "codigo": "CATALOGO_NO_DISPONIBLE",
                "mensaje": "No se pudo conectar al catalogo"
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    try:
        resultado = consolidar_stock(
            bd,
            reserva_id
        )

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "La reserva no existe":
            codigo = "RESERVA_NO_ENCONTRADA"
            estado_http = status.HTTP_404_NOT_FOUND

        elif mensaje.startswith(
            "No se puede procesar una reserva en estado"
        ):
            codigo = "CONFLICTO_RESERVA"
            estado_http = status.HTTP_409_CONFLICT

        else:
            codigo = "DATOS_INVALIDOS"
            estado_http = status.HTTP_400_BAD_REQUEST

        return Response(
            {
                "codigo": codigo,
                "mensaje": mensaje
            },
            status=estado_http
        )

    except RuntimeError:
        return Response(
            {
                "codigo": "CONFLICTO_STOCK",
                "mensaje": "No fue posible completar la consolidacion"
            },
            status=status.HTTP_409_CONFLICT
        )

    except PyMongoError:
        return Response(
            {
                "codigo": "CATALOGO_NO_DISPONIBLE",
                "mensaje": "No se pudo procesar la consolidacion"
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    return Response(
        {
            "reserva_id": resultado["reserva_id"],
            "estado": resultado["estado"],
            "ya_procesada": resultado["ya_procesada"]
        },
        status=status.HTTP_200_OK
    )


class LiberarReservaSerializer(serializers.Serializer):
    motivo = serializers.ChoiceField(
        choices=[
            "PAGO_RECHAZADO",
            "PAGO_CANCELADO",
            "VENCIMIENTO_CONCILIADO",
        ]
    )


@api_view(["POST"])
@authentication_classes([AutenticacionInterna])
@permission_classes([IsAuthenticated])
def liberar_reserva(request, reserva_id):
    """
    Libera una reserva autorizada por Comercio.
    No permite liberar reservas consolidadas.
    """

    datos = LiberarReservaSerializer(data=request.data)

    if not datos.is_valid():
        return Response(
            {
                "codigo": "DATOS_INVALIDOS",
                "mensaje": "Motivo de liberacion invalido",
                "detalles": datos.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        bd = obtener_bd()

    except (RuntimeError, PyMongoError):
        return Response(
            {
                "codigo": "CATALOGO_NO_DISPONIBLE",
                "mensaje": "No se pudo conectar al catalogo"
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    try:
        resultado = liberar_stock(
            bd,
            reserva_id,
            datos.validated_data["motivo"]
        )

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "La reserva no existe":
            codigo = "RESERVA_NO_ENCONTRADA"
            estado_http = status.HTTP_404_NOT_FOUND

        elif (
            mensaje == "La reserva tiene otro motivo"
            or mensaje.startswith(
                "No se puede procesar una reserva en estado"
            )
            or mensaje in (
                "La reserva no contiene productos",
                "Cantidad reservada invalida"
            )
        ):
            codigo = "CONFLICTO_RESERVA"
            estado_http = status.HTTP_409_CONFLICT

        else:
            codigo = "DATOS_INVALIDOS"
            estado_http = status.HTTP_400_BAD_REQUEST

        return Response(
            {
                "codigo": codigo,
                "mensaje": mensaje
            },
            status=estado_http
        )

    except PyMongoError:
        return Response(
            {
                "codigo": "CATALOGO_NO_DISPONIBLE",
                "mensaje": "No se pudo procesar la liberacion"
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    except RuntimeError:
        return Response(
            {
                "codigo": "CONFLICTO_STOCK",
                "mensaje": "No fue posible liberar el inventario"
            },
            status=status.HTTP_409_CONFLICT
        )

    return Response(
        {
            "reserva_id": resultado["reserva_id"],
            "estado": resultado["estado"],
            "ya_procesada": resultado["ya_procesada"]
        },
        status=status.HTTP_200_OK
    )
