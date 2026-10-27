
from pymongo.errors import PyMongoError

from rest_framework.decorators import (
    api_view,
    permission_classes
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .mongo import obtener_bd


@api_view(["GET"])
@permission_classes([AllowAny])
def consultar_producto(request, producto_id):
    """
    Consulta los datos necesarios para Comercio.
    Solo devuelve productos activos.
    """

    try:
        producto = obtener_bd().productos.find_one(
            {
                "id": producto_id,
                "activo": True
            },

            {
                "_id": 0,
                "id": 1,
                "nombre": 1,
                "precio": 1,
                "stock.disponible": 1,
                "activo": 1,
                "imagenes": 1,
                "imagenes_accesibles": 1
            }

        )

    except (PyMongoError, RuntimeError):
        return Response(
            {
                "codigo": "CATALOGO_NO_DISPONIBLE",
                "mensaje": "No se pudo consultar el catálogo"
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    if producto is None:
        return Response(
            {
                "codigo": "PRODUCTO_NO_ENCONTRADO",
                "mensaje": "El producto no existe o está inactivo"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    precio = producto.get("precio")
    stock = producto.get("stock", {})
    disponible = (
        stock.get("disponible")
        if isinstance(stock, dict)
        else None
    )

    if (
        type(precio) not in (int, float)
        or precio <= 0
        or type(disponible) is not int
        or disponible < 0
    ):
        return Response(
            {
                "codigo": "DATOS_PRODUCTO_INVALIDOS",
                "mensaje": "El inventario del producto es inválido"
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


    return Response(
        {
            "id": producto["id"],
            "nombre": producto["nombre"],
            "precio": precio,
            "moneda": "CLP",
            "stock_disponible": disponible,
            "activo": True,
            "imagenes": producto.get("imagenes") or [],
            "imagenes_accesibles": (
                producto.get("imagenes_accesibles") or []
            ),
        },
        status=status.HTTP_200_OK
    )
