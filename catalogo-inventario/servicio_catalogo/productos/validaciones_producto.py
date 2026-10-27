
from decimal import Decimal, InvalidOperation


def validar_precio(precio):
    """El precio debe ser numerico y mayor que cero."""

    if isinstance(precio, bool):
        raise ValueError("El precio debe ser mayor que cero")

    try:
        valor = Decimal(str(precio))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("El precio debe ser numerico")

    if not valor.is_finite() or valor <= 0:
        raise ValueError("El precio debe ser mayor que cero")

    return valor


def validar_stock(stock):
    """El stock debe ser entero y no negativo."""

    if type(stock) is not int or stock < 0:
        raise ValueError(
            "El stock debe ser un entero no negativo"
        )

    return stock


def validar_imagenes(imagenes):
    """Un producto debe contener entre 4 y 6 imagenes."""

    if not isinstance(imagenes, list):
        raise ValueError(
            "Las imagenes deben enviarse en una lista"
        )

    if not 4 <= len(imagenes) <= 6:
        raise ValueError(
            "El producto debe contener entre 4 y 6 imagenes"
        )

    return imagenes
