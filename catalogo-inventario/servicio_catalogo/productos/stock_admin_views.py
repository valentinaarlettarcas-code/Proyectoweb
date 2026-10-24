"""RF-19: ajuste atomico de stock fisico con auditoria en MongoDB.

Stock fisico = stock.disponible + stock.reservado.
Requiere una instalacion MongoDB que admita transacciones multidocumento.
La cabecera X-Admin-Id es identidad DECLARADA, NO verificada por el token temporal.
"""
import re
from datetime import datetime, timezone

from pymongo.errors import PyMongoError
from rest_framework import serializers, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .admin_views import AutenticacionAdministrativaTemporal
from .mongo import obtener_bd


class AjusteStockSerializer(serializers.Serializer):
    stock_fisico = serializers.IntegerField(min_value=0)
    motivo = serializers.CharField(min_length=3, max_length=300, allow_blank=False)


class AjusteRechazado(Exception):
    def __init__(self, codigo, mensaje, estado):
        super().__init__(mensaje)
        self.codigo = codigo
        self.mensaje = mensaje
        self.estado = estado


def _ajustar_en_transaccion(db, producto_id, stock_nuevo, motivo, usuario, session):
    producto = db.productos.find_one({"id": producto_id}, session=session)
    if producto is None:
        raise AjusteRechazado(
            "PRODUCTO_NO_ENCONTRADO", "El producto no existe", 404
        )

    stock = producto.get("stock", {})
    disponible = stock.get("disponible")
    reservado = stock.get("reservado")
    if (type(disponible) is not int or type(reservado) is not int
            or disponible < 0 or reservado < 0):
        raise AjusteRechazado(
            "STOCK_INCONSISTENTE", "El stock del producto es invalido", 409
        )

    anterior = disponible + reservado
    if stock_nuevo < reservado:
        raise AjusteRechazado(
            "STOCK_INFERIOR_A_RESERVADO",
            "El stock fisico no puede ser inferior al reservado", 409
        )
    if stock_nuevo == anterior:
        raise AjusteRechazado(
            "SIN_CAMBIOS", "El stock nuevo es igual al actual", 400
        )

    nuevo_disponible = stock_nuevo - reservado
    # Las reservas usan update_one sobre el mismo documento: una transaccion
    # concurrente producira conflicto de escritura o hara reintentar el ajuste.
    cambio = db.productos.update_one(
        {
            "_id": producto["_id"],
            "stock.disponible": disponible,
            "stock.reservado": reservado,
        },
        {"$set": {"stock.disponible": nuevo_disponible}},
        session=session,
    )
    if cambio.matched_count != 1:
        raise AjusteRechazado(
            "CONFLICTO_STOCK", "El stock cambio durante el ajuste", 409
        )

    registro = {
        "producto_id": producto_id,
        "usuario_id_reportado": usuario,
        "origen_identidad": "cabecera_temporal_no_verificada",
        "fecha": datetime.now(timezone.utc),
        "stock_fisico_anterior": anterior,
        "stock_fisico_nuevo": stock_nuevo,
        "stock_reservado": reservado,
        "stock_disponible_anterior": disponible,
        "stock_disponible_nuevo": nuevo_disponible,
        "motivo": motivo,
    }
    db.ajustes_stock.insert_one(registro, session=session)
    return {
        "producto_id": producto_id,
        "stock_fisico_anterior": anterior,
        "stock_fisico_nuevo": stock_nuevo,
        "stock_reservado": reservado,
        "stock_disponible_nuevo": nuevo_disponible,
        "usuario_id_reportado": usuario,
        "fecha": registro["fecha"].isoformat(),
        "motivo": motivo,
    }


@api_view(["POST"])
@authentication_classes([AutenticacionAdministrativaTemporal])
@permission_classes([IsAuthenticated])
def ajustar_stock_admin(request, producto_id):
    """POST /api/admin/productos/<id>/ajustar-stock/."""
    serializador = AjusteStockSerializer(data=request.data)
    if not serializador.is_valid():
        return Response(
            {"codigo": "DATOS_INVALIDOS", "detalles": serializador.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    usuario = request.headers.get("X-Admin-Id", "").strip()
    if not re.fullmatch(r"[A-Za-z0-9_.@-]{1,100}", usuario):
        return Response(
            {"codigo": "ADMIN_ID_REQUERIDO",
             "mensaje": "Indicar X-Admin-Id del administrador para auditoria"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        bd = obtener_bd()
        with bd.client.start_session() as sesion:
            resultado = sesion.with_transaction(
                lambda s: _ajustar_en_transaccion(
                    bd,
                    producto_id,
                    serializador.validated_data["stock_fisico"],
                    serializador.validated_data["motivo"],
                    usuario,
                    s,
                )
            )
    except AjusteRechazado as error:
        return Response(
            {"codigo": error.codigo, "mensaje": error.mensaje},
            status=error.estado,
        )
    except (PyMongoError, RuntimeError):
        return Response(
            {"codigo": "CATALOGO_NO_DISPONIBLE",
             "mensaje": "No se pudo confirmar el ajuste de stock"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return Response(resultado, status=status.HTTP_200_OK)
