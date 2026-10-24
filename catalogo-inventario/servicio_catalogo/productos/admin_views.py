"""HU-08: creacion de productos (inicio del panel administrativo)."""

import os
from hmac import compare_digest

from pymongo.errors import DuplicateKeyError, PyMongoError
from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .admin_serializers import (
    CrearProductoSerializer,
    EditarProductoSerializer,
)
from .mongo import obtener_bd

from pymongo import ReturnDocument

class UsuarioAdministrativoInterno:
    is_authenticated = True


class AutenticacionAdministrativaTemporal(BaseAuthentication):
    """Token administrativo de desarrollo, NO sustituye verificar-token de Gestion."""

    def authenticate(self, request):
        encabezado = request.headers.get("Authorization", "")
        esquema, separador, token = encabezado.partition(" ")
        if esquema.lower() != "bearer" or not separador or not token:
            return None

        esperado = os.environ.get("CATALOGO_ADMIN_TOKEN")
        if not esperado:
            raise AuthenticationFailed("Autenticacion administrativa no configurada")
        if not compare_digest(token, esperado):
            raise AuthenticationFailed("Credenciales administrativas invalidas")
        return (UsuarioAdministrativoInterno(), None)

    def authenticate_header(self, request):
        return "Bearer"


@api_view(["POST"])
@authentication_classes([AutenticacionAdministrativaTemporal])
@permission_classes([IsAuthenticated])
def crear_producto(request):
    serializador = CrearProductoSerializer(data=request.data)
    if not serializador.is_valid():
        return Response(
            {"codigo": "DATOS_INVALIDOS", "detalles": serializador.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    datos = serializador.validated_data
    documento = {
        "id": datos["id"],
        "nombre": datos["nombre"],
        "descripcion": datos["descripcion"],
        "precio": datos["precio"],
        "categoria": datos["categoria"],
        "imagenes": datos["imagenes"],
        "stock": {"reservado": 0, "disponible": datos["stock_inicial"]},
        "activo": True,
    }

    try:
        bd = obtener_bd()
        # Chequeo para respuesta amigable; la proteccion real ante concurrencia
        # necesita un indice UNICO sobre productos.id en MongoDB.
        if bd.productos.find_one({"id": documento["id"]}, {"_id": 1}):
            return Response(
                {"codigo": "PRODUCTO_DUPLICADO", "mensaje": "El ID ya existe"},
                status=status.HTTP_409_CONFLICT,
            )
        bd.productos.insert_one(documento)
    except DuplicateKeyError:
        return Response(
            {"codigo": "PRODUCTO_DUPLICADO", "mensaje": "El ID ya existe"},
            status=status.HTTP_409_CONFLICT,
        )
    except (PyMongoError, RuntimeError):
        return Response(
            {"codigo": "CATALOGO_NO_DISPONIBLE", "mensaje": "No se pudo crear el producto"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return Response(
        {
            "id": documento["id"],
            "nombre": documento["nombre"],
            "precio": documento["precio"],
            "moneda": "CLP",
            "stock": documento["stock"],
            "imagenes": documento["imagenes"],
            "activo": True,
        },
        status=status.HTTP_201_CREATED,
    )


# RF17: Listado administrativo de productos.

@api_view(["GET"])
@authentication_classes([AutenticacionAdministrativaTemporal])
@permission_classes([IsAuthenticated])
def listar_productos_admin(request):
    """
    Lista los productos registrados en MongoDB.

    Incluye productos activos e inactivos.
    Solo permite el acceso a usuarios administrativos.
    No modifica existencias ni reservas.
    """

    try:
        bd = obtener_bd()

        productos = list(
            bd.productos.find(
                {},
                {
                    "_id": 0,
                    "id": 1,
                    "nombre": 1,
                    "descripcion": 1,
                    "precio": 1,
                    "categoria": 1,
                    "imagenes": 1,
                    "stock": 1,
                    "activo": 1,
                },
            )
        )

        productos.sort(key=lambda producto: producto.get("id", 0))

    except (PyMongoError, RuntimeError):
        return Response(
            {
                "codigo": "CATALOGO_NO_DISPONIBLE",
                "mensaje": "No se pudo obtener el listado de productos",
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return Response(
        {
            "total": len(productos),
            "productos": productos,
        },
        status=status.HTTP_200_OK,
    )


# RF17: Edicion administrativa de productos.

@api_view(["PATCH"])
@authentication_classes([AutenticacionAdministrativaTemporal])
@permission_classes([IsAuthenticated])
def editar_producto_admin(request, producto_id):
    """
    Modifica datos comerciales de un producto.

    No permite modificar:
    - ID
    - Stock disponible o reservado
    - Estado activo/inactivo

    Admite productos activos e inactivos.
    """

    serializador = EditarProductoSerializer(data=request.data)

    if not serializador.is_valid():
        return Response(
            {
                "codigo": "DATOS_INVALIDOS",
                "detalles": serializador.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    cambios = dict(serializador.validated_data)

    try:
        bd = obtener_bd()

        producto_actualizado = bd.productos.find_one_and_update(
            {"id": producto_id},
            {"$set": cambios},
            projection={"_id": 0},
            return_document=ReturnDocument.AFTER,
        )

    except (PyMongoError, RuntimeError):
        return Response(
            {
                "codigo": "CATALOGO_NO_DISPONIBLE",
                "mensaje": "No se pudo actualizar el producto",
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    if producto_actualizado is None:
        return Response(
            {
                "codigo": "PRODUCTO_NO_ENCONTRADO",
                "mensaje": "El producto no existe",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(
        producto_actualizado,
        status=status.HTTP_200_OK,
    )


# RF18: Desactivacion logica de productos.

@api_view(["PATCH"])
@authentication_classes([AutenticacionAdministrativaTemporal])
@permission_classes([IsAuthenticated])
def desactivar_producto_admin(request, producto_id):
    """
    Desactiva un producto sin eliminarlo de MongoDB.

    Conserva:
    - Identificador
    - Datos comerciales
    - Stock disponible
    - Stock reservado

    La operacion es idempotente:
    desactivar dos veces no genera un error.
    """

    try:
        productos = obtener_bd().productos

        # Desactivar solo si actualmente esta activo.
        producto = productos.find_one_and_update(
            {
                "id": producto_id,
                "activo": True,
            },
            {
                "$set": {
                    "activo": False,
                }
            },
            projection={"_id": 0},
            return_document=ReturnDocument.AFTER,
        )

        desactivado_ahora = producto is not None

        # Distinguir un producto inexistente de uno ya inactivo.
        if producto is None:
            producto = productos.find_one(
                {"id": producto_id},
                {"_id": 0},
            )

    except (PyMongoError, RuntimeError):
        return Response(
            {
                "codigo": "CATALOGO_NO_DISPONIBLE",
                "mensaje": "No se pudo desactivar el producto",
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    if producto is None:
        return Response(
            {
                "codigo": "PRODUCTO_NO_ENCONTRADO",
                "mensaje": "El producto no existe",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(
        {
            "id": producto_id,
            "activo": producto.get("activo", False),
            "mensaje": (
                "Producto desactivado correctamente"
                if desactivado_ahora
                else "El producto ya estaba desactivado"
            ),
            "stock": producto.get("stock", {}),
        },
        status=status.HTTP_200_OK,
    )
