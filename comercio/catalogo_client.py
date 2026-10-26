import os

import requests


from rest_framework.exceptions import APIException


class CatalogoError(APIException):
    def __init__(self, message, status_code=503):
        self.status_code = status_code
        self.default_detail = message
        super().__init__(detail=message, code=status_code)


def _configuracion():
    base_url = os.environ.get("CATALOGO_API_BASE_URL", "").rstrip("/")
    token = os.environ.get("CATALOGO_INTERNAL_TOKEN", "")

    if not base_url:
        raise CatalogoError("Catálogo no tiene una URL configurada.", 503)

    if not token:
        raise CatalogoError("Falta configurar el acceso interno a Catálogo.", 503)

    return base_url, {"Authorization": f"Bearer {token}",
                      "Accept": "application/json"}


def _post(path, payload=None):
    base_url, headers = _configuracion()

    try:
        response = requests.post(
            f"{base_url}{path}",
            json=payload or {},
            headers=headers,
            timeout=5,
        )
    except requests.RequestException as exc:
        raise CatalogoError("Catálogo no está disponible.", 503) from exc

    if response.status_code not in (200, 201):
        try:
            data = response.json()
            message = data.get("mensaje", "Error al procesar inventario.")
        except (ValueError, AttributeError):
            message = "Catálogo devolvió una respuesta inválida."

        code = response.status_code
        if code >= 500:
            code = 503
        elif code not in (400, 401, 403, 404, 409):
            code = 502

        raise CatalogoError(message, code)

    try:
        return response.json()
    except ValueError as exc:
        raise CatalogoError("Catálogo devolvió una respuesta inválida.", 502) from exc


def reservar(reserva_id, orden_id, productos):
    return _post(
        "/api/reservas/",
        {
            "reserva_id": str(reserva_id),
            "orden_id": str(orden_id),
            "productos": [
                {"producto_id": int(item["producto_id"]),
                 "cantidad": int(item["quantity"])}
                for item in productos
            ],
        },
    )


def consolidar(reserva_id):
    return _post(f"/api/reservas/{reserva_id}/consolidar/")


def liberar(reserva_id, motivo):
    motivos_validos = {
        "PAGO_RECHAZADO",
        "PAGO_CANCELADO",
        "VENCIMIENTO_CONCILIADO",
    }
    if motivo not in motivos_validos:
        raise ValueError("Motivo de liberación no válido.")

    return _post(
        f"/api/reservas/{reserva_id}/liberar/",
        {"motivo": motivo},
    )
