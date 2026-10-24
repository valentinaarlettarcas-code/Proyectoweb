
"""
Administracion de productos del microservicio Catalogo.

Funcionalidades:
- Crear productos.
- Listar productos para el administrador.
- Editar datos comerciales.
- Editar imagenes y textos alternativos.
- Desactivar productos sin eliminarlos.

La autenticacion mediante token administrativo es provisional
y debe integrarse posteriormente con el servicio de Gestion.
"""

import os
from hmac import compare_digest

from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError

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

from .admin_serializers import (
    CrearProductoSerializer,
    EditarProductoSerializer,
)
from .mongo import obtener_bd


# ============================================================
# AUTENTICACION ADMINISTRATIVA PROVISIONAL
# ============================================================

class UsuarioAdministrativoInterno:
    """
    Representa temporalmente a un administrador autenticado.

    Se reemplazara al integrar la autenticacion de Gestion.
    """

    is_authenticated = True


class AutenticacionAdministrativaTemporal(BaseAuthentication):
    """
    Comprueba el token administrativo configurado en el entorno.

    Encabezado esperado:
    Authorization: Bearer TOKEN
    """

    def authenticate(self, request):
        encabezado = request.headers.get("Authorization", "")

        esquema, separador, token = encabezado.partition(" ")

        if (
            esquema.lower() != "bearer"
            or not separador
            or not token
        ):
            return None

        esperado = os.environ.get("CATALOGO_ADMIN_TOKEN")

        if not esperado:
            raise AuthenticationFailed(
                "Autenticacion administrativa no configurada"
            )

        if not compare_digest(token, esperado):
            raise AuthenticationFailed(
                "Credenciales administrativas invalidas"
            )

        return UsuarioAdministrativoInterno(), None

    def authenticate_header(self, request):
        return "Bearer"


# ============================================================
# RESPUESTAS AUXILIARES
# ============================================================

def respuesta_datos_invalidos(errores):
    """Genera una respuesta uniforme para datos invalidos."""

    return Response(
        {
            "codigo": "DATOS_INVALIDOS",
            "detalles": errores,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


def respuesta_catalogo_no_disponible(mensaje):
    """Respuesta cuando MongoDB no esta disponible."""

    return Response(
        {
            "codigo": "CATALOGO_NO_DISPONIBLE",
            "mensaje": mensaje,
        },
        status=status.HTTP_503_SERVICE_UNAVAILABLE,
    )


def respuesta_producto_no_encontrado():
    """Respuesta cuando un producto no existe."""

    return Response(
        {
            "codigo": "PRODUCTO_NO_ENCONTRADO",
            "mensaje": "El producto no existe",
        },
        status=status.HTTP_404_NOT_FOUND,
    )


# ============================================================
# HU-08: CREACION ADMINISTRATIVA DE PRODUCTOS
# POST /api/productos/
# ============================================================

@api_view(["POST"])
@authentication_classes([AutenticacionAdministrativaTemporal])
@permission_classes([IsAuthenticated])
def crear_producto(request):
    """
    Crea un producto nuevo en MongoDB.

    Valida:
    - Identificador positivo.
    - Nombre y descripcion.
    - Precio positivo.
    - Categoria.
    - Stock inicial no negativo.
    - Entre 4 y 6 imagenes.

    Si se proporcionan textos alternativos, se guardan
    asociados a las URL de cada imagen.
    """

    serializador = CrearProductoSerializer(
        data=request.data
    )

    if not serializador.is_valid():
        return respuesta_datos_invalidos(
            serializador.errors
        )

    datos = serializador.validated_data

    documento = {
        "id": datos["id"],
        "nombre": datos["nombre"],
        "descripcion": datos["descripcion"],
        "precio": datos["precio"],
        "categoria": datos["categoria"],
        "imagenes": datos["imagenes"],
        "stock": {
            "reservado": 0,
            "disponible": datos["stock_inicial"],
        },
        "activo": True,
    }

    # --------------------------------------------------------
    # IMAGENES ACCESIBLES
    # --------------------------------------------------------

    textos = datos.get("textos_alternativos")

    if textos is not None:
        documento["imagenes_accesibles"] = [
            {
                "url": url,
                "texto_alternativo": texto,
            }
            for url, texto in zip(
                datos["imagenes"],
                textos,
                strict=True,
            )
        ]

    # --------------------------------------------------------
    # PERSISTENCIA EN MONGODB
    # --------------------------------------------------------

    try:
        bd = obtener_bd()

        # Comprobacion amigable de ID duplicado.
        # La proteccion real requiere un indice unico en MongoDB.
        existente = bd.productos.find_one(
            {"id": documento["id"]},
            {"_id": 1},
        )

        if existente:
            return Response(
                {
                    "codigo": "PRODUCTO_DUPLICADO",
                    "mensaje": "El ID ya existe",
                },
                status=status.HTTP_409_CONFLICT,
            )

        bd.productos.insert_one(documento)

    except DuplicateKeyError:
        return Response(
            {
                "codigo": "PRODUCTO_DUPLICADO",
                "mensaje": "El ID ya existe",
            },
            status=status.HTTP_409_CONFLICT,
        )

    except (PyMongoError, RuntimeError):
        return respuesta_catalogo_no_disponible(
            "No se pudo crear el producto"
        )

    # Mantener la respuesta de creacion existente.
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


# ============================================================
# RF17: LISTADO ADMINISTRATIVO DE PRODUCTOS
# GET /api/admin/productos/
# ============================================================

@api_view(["GET"])
@authentication_classes([AutenticacionAdministrativaTemporal])
@permission_classes([IsAuthenticated])
def listar_productos_admin(request):
    """
    Lista todos los productos.

    A diferencia de la consulta publica de Comercio,
    incluye productos activos e inactivos.
    """

    try:
        bd = obtener_bd()

        productos = list(
            bd.productos.find(
                {},
                {"_id": 0},
            )
        )

    except (PyMongoError, RuntimeError):
        return respuesta_catalogo_no_disponible(
            "No se pudo consultar el catalogo"
        )

    return Response(
        {
            "total": len(productos),
            "productos": productos,
        },
        status=status.HTTP_200_OK,
    )


# ============================================================
# RF17: EDICION ADMINISTRATIVA DE PRODUCTOS
# PATCH /api/admin/productos/<id>/
# ============================================================

@api_view(["PATCH"])
@authentication_classes([AutenticacionAdministrativaTemporal])
@permission_classes([IsAuthenticated])
def editar_producto_admin(request, producto_id):
    """
    Permite actualizar los datos comerciales de un producto.

    Campos editables:
    - nombre
    - descripcion
    - precio
    - categoria
    - imagenes
    - textos_alternativos

    No permite cambiar mediante esta operacion:
    - id
    - stock
    - activo

    Las imagenes y sus textos alternativos deben enviarse
    conjuntamente, manteniendo una correspondencia uno a uno.
    """

    serializador = EditarProductoSerializer(
        data=request.data
    )

    if not serializador.is_valid():
        return respuesta_datos_invalidos(
            serializador.errors
        )

    # --------------------------------------------------------
    # PREPARACION DE LOS CAMPOS EDITABLES
    # --------------------------------------------------------

    cambios = dict(serializador.validated_data)

    # Este campo se transforma en objetos accesibles.
    # No se almacena como una lista independiente.
    textos = cambios.pop(
        "textos_alternativos",
        None,
    )

    if textos is not None:
        imagenes = cambios["imagenes"]

        cambios["imagenes_accesibles"] = [
            {
                "url": url,
                "texto_alternativo": texto,
            }
            for url, texto in zip(
                imagenes,
                textos,
                strict=True,
            )
        ]

    # Proteccion adicional para mantener separado RF19.
    campos_prohibidos = {
        "id",
        "stock",
        "stock_inicial",
        "activo",
    }

    if campos_prohibidos.intersection(cambios):
        return respuesta_datos_invalidos({
            "campos": (
                "No se permite modificar el identificador, "
                "el stock ni el estado desde esta operacion."
            )
        })

    if not cambios:
        return respuesta_datos_invalidos({
            "campos": "No se proporcionaron campos para editar."
        })

    # --------------------------------------------------------
    # ACTUALIZACION EN MONGODB
    # --------------------------------------------------------

    try:
        bd = obtener_bd()

        producto_actualizado = (
            bd.productos.find_one_and_update(
                {
                    "id": producto_id,
                },
                {
                    "$set": cambios,
                },
                projection={
                    "_id": 0,
                },
                return_document=ReturnDocument.AFTER,
            )
        )

    except (PyMongoError, RuntimeError):
        return respuesta_catalogo_no_disponible(
            "No se pudo actualizar el producto"
        )

    if producto_actualizado is None:
        return respuesta_producto_no_encontrado()

    # La respuesta refleja el producto resultante.
    # No se modifica la API publica utilizada por Comercio.
    resultado = {
        clave: valor
        for clave, valor in producto_actualizado.items()
        if clave != "_id"
    }

    return Response(
        resultado,
        status=status.HTTP_200_OK,
    )


# ============================================================
# RF18: DESACTIVACION LOGICA DE PRODUCTOS
# PATCH /api/admin/productos/<id>/desactivar/
# ============================================================

@api_view(["PATCH"])
@authentication_classes([AutenticacionAdministrativaTemporal])
@permission_classes([IsAuthenticated])
def desactivar_producto_admin(request, producto_id):
    """
    Desactiva un producto sin eliminar su documento de MongoDB.

    Conserva los datos comerciales y el stock existente.

    La operacion es idempotente:
    desactivar un producto ya inactivo devuelve HTTP 200.
    """

    try:
        productos = obtener_bd().productos

        # Modificar solo los productos que siguen activos.
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
            projection={
                "_id": 0,
            },
            return_document=ReturnDocument.AFTER,
        )

        desactivado_ahora = producto is not None

        # Si no hubo actualizacion, revisar si ya estaba inactivo.
        if producto is None:
            producto = productos.find_one(
                {
                    "id": producto_id,
                },
                {
                    "_id": 0,
                },
            )

    except (PyMongoError, RuntimeError):
        return respuesta_catalogo_no_disponible(
            "No se pudo desactivar el producto"
        )

    if producto is None:
        return respuesta_producto_no_encontrado()

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
