"""Simulacion compartida del verificador de Gestion, solo para pruebas."""
import json
import os
from unittest.mock import patch
from urllib.error import HTTPError

URL_PRUEBA = "http://127.0.0.1:8001/api/usuarios/verificar-token/"


def configurar_autenticacion_de_prueba(caso):
    """Instala una respuesta HTTP simulada ADMIN/ACTIVO sin usar la red."""
    entorno = patch.dict(os.environ, {"GESTION_VERIFY_TOKEN_URL": URL_PRUEBA})
    entorno.start()
    caso.addCleanup(entorno.stop)

    parche = patch("productos.autenticacion_gestion.build_opener")
    constructor = parche.start()
    caso.addCleanup(parche.stop)

    http = constructor.return_value.open
    http.return_value.__enter__.return_value.read.return_value = json.dumps({
        "valido": True,
        "usuario": {
            "id": 55,
            "email": "admin-prueba@example.invalid",
            "rol": "ADMIN",
            "estado": "ACTIVO",
        },
    }).encode("utf-8")
    return http


def rechazar_token_de_prueba(http):
    """Simula la respuesta oficial de Gestion ante un token incorrecto."""
    http.side_effect = HTTPError(URL_PRUEBA, 401, "Unauthorized", None, None)
