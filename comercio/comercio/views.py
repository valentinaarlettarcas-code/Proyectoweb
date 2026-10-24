from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .serializers import OrderSerializer
from .autenticacion import verificar_token_cliente


class CrearOrdenView(APIView):
    permission_classes = []

    def post(self, request):
        # 1. Validar token y obtener ID del cliente usando la función centralizada
        cliente_id = verificar_token_cliente(request)

        # 2. Idempotencia: Verificar si ya existe una orden con ese checkout_id para este cliente
        checkout_id = request.data.get("checkout_id")
        if checkout_id:
            orden_existente = Order.objects.filter(cliente_id=cliente_id, checkout_id=checkout_id).first()
            if orden_existente:
                # Si existe, la devolvemos inmediatamente en lugar de duplicarla o dar error
                return Response(OrderSerializer(orden_existente).data, status=status.HTTP_200_OK)

        # 3. Si no existe, creamos la orden inyectando el cliente_id verificado
        serializer = OrderSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save(cliente_id=cliente_id)
        
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class DetalleOrdenView(APIView):
    permission_classes = []

    def get(self, request, pk):
        # 1. Validar token y obtener ID del cliente
        cliente_id = verificar_token_cliente(request)

        # 2. Buscar la orden asegurando que pertenezca al cliente logueado
        order = get_object_or_404(Order, pk=pk, cliente_id=cliente_id)
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)