from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        # Los campos se envian o reciben en el JSON
        fields = ['producto_id', 'historical_product_name', 'historical_price', 'moneda', 'quantity', 'subtotal']

class OrderSerializer(serializers.ModelSerializer):
    # Agrupamos los ítems para que se puedan enviar junto con la orden en un solo JSON
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'cliente_id', 'checkout_id', 'status', 'total_amount', 'moneda', 'created_at', 'items']
        # El cliente_id y status los define el backend, no el usuario, por eso son de solo lectura!!
        read_only_fields = ['id', 'cliente_id', 'status', 'created_at']

    def create(self, validated_data):
        # Def que guarda la orden y sus ítems en la base de datos al mismo tiempo
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order