
from datetime import datetime, timezone

from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
from pymongo.read_preferences import ReadPreference


MOTIVOS_LIBERACION = {
    "PAGO_RECHAZADO",
    "PAGO_CANCELADO",
    "VENCIMIENTO_CONCILIADO"
}


def _cambiar_estado(db, reserva_id, nuevo_estado, motivo=None):
    """
    Actualiza existencias y reserva en una transaccion.
    Solo admite reservas que estan en estado RESERVADA.
    """

    if not isinstance(reserva_id, str) or not reserva_id.strip():
        raise ValueError("Identificador de reserva invalido")

    if nuevo_estado == "LIBERADA":
        if motivo not in MOTIVOS_LIBERACION:
            raise ValueError("Motivo de liberacion invalido")

    def operacion(session):
        reserva = db.reservas.find_one(
            {"_id": reserva_id},
            session=session
        )

        if reserva is None:
            raise ValueError("La reserva no existe")

        estado = reserva["estado"]

        # Repetir una operacion ya realizada no modifica stock.
        if estado == nuevo_estado:
            if (nuevo_estado == "LIBERADA" and
                    reserva.get("motivo_liberacion") != motivo):
                raise ValueError("La reserva tiene otro motivo")

            return {
                "reserva_id": reserva_id,
                "estado": estado,
                "ya_procesada": True
            }

        if estado != "RESERVADA":
            raise ValueError(
                f"No se puede procesar una reserva en estado {estado}"
            )

        fecha = datetime.now(timezone.utc)

        productos = reserva.get("productos", [])
        if not productos:
            raise ValueError("La reserva no contiene productos")

        for producto in productos:
            producto_id = producto["producto_id"]
            cantidad = producto["cantidad"]

            if type(cantidad) is not int or cantidad <= 0:
                raise ValueError("Cantidad reservada invalida")

            filtro = {
                "id": producto_id,
                "stock.reservado": {"$gte": cantidad},
                "stock.disponible": {"$gte": 0}
            }

            if nuevo_estado == "CONSOLIDADA":
                # La venta reduce el stock físico total, no el disponible.
                cambios = {
                    "$inc": {"stock.reservado": -cantidad}
                }
            else:
                # Devolver unidades reservadas al stock disponible.
                cambios = {
                    "$inc": {
                        "stock.reservado": -cantidad,
                        "stock.disponible": cantidad
                    }
                }

            resultado = db.productos.update_one(
                filtro,
                cambios,
                session=session
            )

            if resultado.modified_count != 1:
                raise RuntimeError(
                    f"No fue posible actualizar producto {producto_id}"
                )

            db.movimientos_inventario.insert_one(
                {
                    "_id": f"{nuevo_estado}:{reserva_id}:{producto_id}",
                    "reserva_id": reserva_id,
                    "orden_id": reserva["orden_id"],
                    "producto_id": producto_id,
                    "cantidad": cantidad,
                    "tipo": nuevo_estado,
                    "fecha": fecha
                },
                session=session
            )

        cambios_reserva = {
            "estado": nuevo_estado,
            "fecha_finalizacion": fecha
        }

        if nuevo_estado == "LIBERADA":
            cambios_reserva["motivo_liberacion"] = motivo

        resultado = db.reservas.update_one(
            {
                "_id": reserva_id,
                "estado": "RESERVADA"
            },
            {"$set": cambios_reserva},
            session=session
        )

        if resultado.modified_count != 1:
            raise RuntimeError("No se pudo actualizar la reserva")

        return {
            "reserva_id": reserva_id,
            "estado": nuevo_estado,
            "ya_procesada": False
        }

    with db.client.start_session() as session:
        return session.with_transaction(
            operacion,
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
            read_preference=ReadPreference.PRIMARY
        )


def consolidar_stock(db, reserva_id):
    """
    Ejecutar exclusivamente despues de verificar
    el pago desde el backend autorizado.
    """
    return _cambiar_estado(
        db,
        reserva_id,
        "CONSOLIDADA"
    )


def liberar_stock(db, reserva_id, motivo):
    """
    Liberar solo con rechazo, cancelacion o vencimiento
    previamente verificado por el servicio de Comercio.
    """
    return _cambiar_estado(
        db,
        reserva_id,
        "LIBERADA",
        motivo
    )
