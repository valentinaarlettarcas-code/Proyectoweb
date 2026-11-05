import os
from decimal import Decimal

import requests
from django.db import transaction
from rest_framework import serializers

from .catalogo_client import CatalogoError, reservar
from .models import Order, OrderItem


class OrderItemInputSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1, max_value=100)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "producto_id",
            "historical_product_name",
            "historical_price",
            "moneda",
            "quantity",
            "subtotal",
        ]
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    # El cliente solo entrega producto y cantidad; nunca precio, subtotal ni total.
    items = OrderItemInputSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "cliente_id", "checkout_id", "status",
            "total_amount", "moneda", "created_at", "items",
        ]
        read_only_fields = ["id", "cliente_id", "status", "created_at", "total_amount", "moneda"]

    def validate_items(self, items):
        ids = [item["producto_id"] for item in items]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("No repitas un producto; combina sus cantidades.")
        if not items:
            raise serializers.ValidationError("La orden debe incluir al menos un producto.")
        return items

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        catalog_base = os.environ.get("CATALOGO_API_BASE_URL", "").rstrip("/")
        if not catalog_base:
            raise serializers.ValidationError({"items": "Falta configurar CATALOGO_API_BASE_URL."})

        # Precios y disponibilidad se consultan en Catálogo; el frontend no puede imponerlos.
        productos = []
        total = Decimal("0")
        for item in items_data:
            try:
                response = requests.get(
                    f"{catalog_base}/api/productos/{item['producto_id']}/",
                    timeout=5,
                )
            except requests.RequestException:
                raise serializers.ValidationError({"items": "Catálogo no está disponible; intenta nuevamente."})

            if response.status_code == 404:
                raise serializers.ValidationError({"items": f"Producto {item['producto_id']} no existe o está inactivo."})
            if response.status_code != 200:
                raise serializers.ValidationError({"items": "No se pudo validar un producto en Catálogo."})

            try:
                product = response.json()
                price = Decimal(str(product["precio"]))
                name = str(product["nombre"])
                currency = str(product.get("moneda", "CLP"))
                available = int(product["stock_disponible"])
            except (ValueError, TypeError, KeyError):
                raise serializers.ValidationError({"items": "Catálogo devolvió datos inválidos."})

            if price <= 0 or available < item["quantity"] or currency != "CLP":
                raise serializers.ValidationError({"items": f"Precio, moneda o stock inválido para el producto {item['producto_id']}."})
            subtotal = price * item["quantity"]
            total += subtotal
            productos.append({
                "producto_id": str(item["producto_id"]),
                "name": name,
                "price": price,
                "currency": currency,
                "quantity": item["quantity"],
                "subtotal": subtotal,
            })

        # Crear la orden y sus líneas antes de solicitar la reserva remota.
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
                    producto_id=item["producto_id"],
                    historical_product_name=item["name"],
                    historical_price=item["price"],
                    moneda=item["currency"],
                    quantity=item["quantity"],
                    subtotal=item["subtotal"],
                )
                for item in productos
            ])

        # La reserva usa un identificador determinista para facilitar reintentos.
        reserva_id = f"orden-{order.pk}"
        try:
            reservar(
                reserva_id=reserva_id,
                orden_id=order.pk,
                productos=[
                    {
                        "producto_id": item["producto_id"],
                        "quantity": item["quantity"],
                    }
                    for item in productos
                ],
            )
        except CatalogoError as exc:
            # Una orden sin reserva no debe quedar habilitada para pago.
            nuevo_estado = (
                "RECHAZADA"
                if exc.status_code in (400, 409)
                else "REVISION_REQUERIDA"
            )
            Order.objects.filter(pk=order.pk).update(status=nuevo_estado)
            order.status = nuevo_estado
            raise

        return order

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["items"] = OrderItemSerializer(instance.items.all(), many=True).data
        return data
