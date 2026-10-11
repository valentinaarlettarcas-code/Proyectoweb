
from datetime import datetime, timedelta, timezone

from pymongo.errors import DuplicateKeyError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
from pymongo.read_preferences import ReadPreference
from pymongo import ASCENDING


def configurar_indices_reservas(db):
    """
    Impide crear dos reservas para una misma orden.
    Debe ejecutarse al inicializar el servicio.
    """
    db.reservas.create_index(
        [("orden_id", ASCENDING)],
        unique=True,
        name="orden_id_unico"
    )


def reservar_stock(db, reserva_id, orden_id, productos):
    """
    Reserva todos los productos de una orden.
    Si falla uno, no se reserva ninguno.
    """

    if not isinstance(reserva_id, str) or not reserva_id.strip():
        raise ValueError("Identificador de reserva inválido")

    if not isinstance(orden_id, str) or not orden_id.strip():
        raise ValueError("Identificador de orden inválido")

    if not isinstance(productos, list) or not productos:
        raise ValueError("La reserva debe contener productos")

    lineas = []
    identificadores = set()

    for producto in productos:
        if not isinstance(producto, dict):
            raise ValueError("Producto inválido")

        producto_id = producto.get("producto_id")
        cantidad = producto.get("cantidad")

        if type(producto_id) is not int or producto_id <= 0:
            raise ValueError("Identificador de producto inválido")

        if type(cantidad) is not int or cantidad <= 0:
            raise ValueError("La cantidad debe ser un entero positivo")

        if producto_id in identificadores:
            raise ValueError("Producto repetido en la reserva")

        identificadores.add(producto_id)
        lineas.append({
            "producto_id": producto_id,
            "cantidad": cantidad
        })

    lineas.sort(key=lambda item: item["producto_id"])

    def operacion(session):

        existente = db.reservas.find_one(
            {"_id": reserva_id},
            session=session
        )

        if existente:
            if (existente["orden_id"] != orden_id or
                    existente["productos"] != lineas):
                raise ValueError("Reserva reutilizada con otros datos")

            return existente


        # Evitar dos reservas diferentes para la misma orden
        reserva_orden = db.reservas.find_one(
            {"orden_id": orden_id},
            session=session
        )

        if reserva_orden is not None:
            raise ValueError(
                "La orden ya tiene una reserva con otro identificador"
            )


        for producto in lineas:

            cantidad = producto["cantidad"]

            resultado = db.productos.update_one(
                {
                    "id": producto["producto_id"],
                    "activo": True,
                    "stock_reservado": {"$gte": 0},
                    "$expr": {
                        "$gte": [
                            {
                                "$subtract": [
                                    "$stock_fisico",
                                    "$stock_reservado"
                                ]
                            },
                            cantidad
                        ]
                    }
                },
                {
                    "$inc": {
                        "stock_reservado": cantidad
                    }
                },
                session=session
            )

            if resultado.modified_count != 1:
                raise ValueError(
                    f"Stock insuficiente o producto inactivo: "
                    f"{producto['producto_id']}"
                )

        ahora = datetime.now(timezone.utc)

        reserva = {
            "_id": reserva_id,
            "orden_id": orden_id,
            "productos": lineas,
            "estado": "RESERVADA",
            "fecha_creacion": ahora,
            "fecha_expiracion": ahora + timedelta(minutes=15),
            "fecha_finalizacion": None
        }

        db.reservas.insert_one(reserva, session=session)

        return reserva

    try:
        with db.client.start_session() as session:
            return session.with_transaction(
                operacion,
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority"),
                read_preference=ReadPreference.PRIMARY
            )

    except DuplicateKeyError:
        # Otra solicitud pudo crear la misma reserva.
        existente = db.reservas.find_one({"_id": reserva_id})

        if (existente and
                existente["orden_id"] == orden_id and
                existente["productos"] == lineas):
            return existente

        raise ValueError("Identificador de reserva duplicado")

