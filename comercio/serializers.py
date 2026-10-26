import os
from decimal import Decimal

import requests
from django.db import transaction
from rest_framework import serializers

from .catalogo_client import CatalogoError, reservar
from .models import Order, OrderItem


class OrderItemInputSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "producto_id",
            "historical_product_name",
            "historical_price",
            "moneda",
            "quantity",
            "subtotal",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemInputSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "cliente_id",
            "checkout_id",
            "status",
            "total_amount",
            "moneda",
            "created_at",
            "items",
        ]
        read_only_fields = [
            "id",
            "cliente_id",
            "status",
            "created_at",
            "total_amount",
            "moneda",
        ]

    def validate_items(self, items):
        ids = [item["producto_id"] for item in items]

        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                "No repitas un producto; combina sus cantidades."
            )

        if not items:
            raise serializers.ValidationError(
                "La orden debe incluir al menos un producto."
            )

        return items

    def create(self, validated_data):
        items_data = validated_data.pop("items")

        catalog_base = os.environ.get(
            "CATALOGO_API_BASE_URL", ""
        ).rstrip("/")

        if not catalog_base:
            raise CatalogoError(
                "Falta configurar CATALOGO_API_BASE_URL.",
                503,
            )

        productos = []
        total = Decimal("0")

        for item in items_data:
            try:
                response = requests.get(
                    f"{catalog_base}/api/productos/{item['producto_id']}/",
                    timeout=5,
                )
            except requests.RequestException as exc:
                raise CatalogoError(
                    "Catálogo no está disponible; intenta nuevamente.",
                    503,
                ) from exc

            if response.status_code == 404:
                raise serializers.ValidationError({
                    "items": (
                        f"Producto {item['producto_id']} "
                        "no existe o está inactivo."
                    )
                })

            if response.status_code != 200:
                if response.status_code >= 500:
                    raise CatalogoError(
                        "Catálogo no está disponible; intenta nuevamente.",
                        503,
                    )

                raise serializers.ValidationError({
                    "items": "No se pudo validar un producto en Catálogo."
                })

            try:
                product = response.json()
                price = Decimal(str(product["precio"]))
                name = str(product["nombre"])
                currency = str(product.get("moneda", "CLP"))
                available = int(product["stock_disponible"])
            except (ValueError, TypeError, KeyError):
                raise CatalogoError(
                    "Catálogo devolvió datos inválidos.",
                    502,
                )

            if (
                price <= 0
                or available < item["quantity"]
                or currency != "CLP"
            ):
                raise serializers.ValidationError({
                    "items": (
                        f"Precio, moneda o stock inválido para el producto "
                        f"{item['producto_id']}."
                    )
                })

            subtotal = price * item["quantity"]
            total += subtotal

            productos.append({
                "producto_id": item["producto_id"],
                "name": name,
                "price": price,
                "currency": currency,
                "quantity": item["quantity"],
                "subtotal": subtotal,
            })

        with transaction.atomic():
            order = Order.objects.create(
                **validated_data,
                status="PENDIENTE_PAGO",
                total_amount=total,
                moneda="CLP",
            )

            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    producto_id=str(item["producto_id"]),
                    historical_product_name=item["name"],
                    historical_price=item["price"],
                    moneda=item["currency"],
                    quantity=item["quantity"],
                    subtotal=item["subtotal"],
                )
                for item in productos
            ])

        reserva_id = f"ORD-{order.pk}"

        try:
            reservar(
                reserva_id=reserva_id,
                orden_id=str(order.pk),
                productos=productos,
            )
        except CatalogoError:
            order.status = "REVISION_REQUERIDA"
            order.save(update_fields=["status", "updated_at"])
            raise

        return order

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["items"] = OrderItemSerializer(
            instance.items.all(),
            many=True,
        ).data
        return data
