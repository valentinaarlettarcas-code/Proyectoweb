
import os
from functools import lru_cache

from pymongo import MongoClient


@lru_cache(maxsize=1)
def obtener_bd():
    """
    Obtiene la base de datos MongoDB del catálogo.
    La conexión se configura mediante una variable
    de entorno y se reutiliza entre solicitudes.
    """

    uri = os.environ.get("CATALOGO_MONGO_URI")

    if not uri:
        raise RuntimeError(
            "Falta configurar CATALOGO_MONGO_URI"
        )

    cliente = MongoClient(
        uri,
        serverSelectionTimeoutMS=3000
    )

    return cliente["catalogo_db"]
