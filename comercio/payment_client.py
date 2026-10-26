import os

import requests
from rest_framework.exceptions import APIException


API_URL = "https:" + "/" + "/" + "api.mercadopago.com"


class PaymentError(APIException):
    status_code = 502
    default_detail = "Error al comunicarse con Mercado Pago."


def _headers():
    token = os.environ.get("MERCADOPAGO_ACCESS_TOKEN", "")
    if not token:
        raise PaymentError("Falta configurar MERCADOPAGO_ACCESS_TOKEN.")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def crear_checkout(order, notification_url=""):
    items = [
        {
            "id": item.producto_id,
            "title": item.historical_product_name,
            "quantity": item.quantity,
            "unit_price": float(item.historical_price),
            "currency_id": item.moneda,
        }
        for item in order.items.all()
    ]

    payload = {
        "items": items,
        "external_reference": str(order.pk),
        "metadata": {"order_id": order.pk},
    }

    if notification_url:
        if not notification_url.startswith("https://"):
            raise PaymentError("La URL del webhook debe utilizar HTTPS.")
        payload["notification_url"] = notification_url

    try:
        response = requests.post(
            f"{API_URL}/checkout/preferences",
            headers=_headers(),
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise PaymentError("No se pudo crear el checkout de pago.") from exc
    except ValueError as exc:
        raise PaymentError("Mercado Pago devolvió una respuesta inválida.") from exc

    if not data.get("id") or not data.get("init_point"):
        raise PaymentError("La respuesta no contiene la URL del checkout.")

    return data
