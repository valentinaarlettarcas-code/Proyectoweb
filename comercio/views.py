import os

import requests
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .serializers import OrderSerializer


def _headers(request):
    token = request.headers.get("Authorization", "")
    return {"Authorization": token, "Accept": "application/json"}


class CrearOrdenView(APIView):
    # La autenticación se verifica consultando Gestión; no se confía en IDs del cliente.
    permission_classes = []

    def post(self, request):
        gestion_url = os.environ.get("GESTION_VERIFY_TOKEN_URL")
        if not gestion_url:
            return Response(
                {"error": "Falta configurar GESTION_VERIFY_TOKEN_URL"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.lower().startswith("token "):
            return Response(
                {"error": "Se requiere Authorization: Token <token>"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            gestion_response = requests.get(
                gestion_url,
                headers=_headers(request),
                timeout=5,
            )
        except requests.RequestException:
            return Response(
                {"error": "Servicio de Gestión no disponible"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        if gestion_response.status_code != 200:
            return Response(
                {"error": "Token inválido o cuenta no activa"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            payload = gestion_response.json()
            usuario = payload.get("usuario", {})
            cliente_id = usuario.get("id")
            activo = usuario.get("estado") == "ACTIVO" or str(usuario.get("estado", "")).lower() == "activo"
        except (ValueError, AttributeError):
            return Response(
                {"error": "Respuesta inválida del servicio de Gestión"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if not payload.get("valido") or not cliente_id or not activo:
            return Response(
                {"error": "Gestión no confirmó un usuario activo"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = OrderSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save(cliente_id=cliente_id)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class DetalleOrdenView(APIView):
    permission_classes = []

    def get(self, request, pk):
        gestion_url = os.environ.get("GESTION_VERIFY_TOKEN_URL")
        if not gestion_url:
            return Response(
                {"error": "Falta configurar GESTION_VERIFY_TOKEN_URL"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.lower().startswith("token "):
            return Response({"error": "Autenticación requerida"}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            resp = requests.get(gestion_url, headers=_headers(request), timeout=5)
        except requests.RequestException:
            return Response({"error": "Servicio de Gestión no disponible"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        if resp.status_code != 200:
            return Response({"error": "Token inválido o cuenta no activa"}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            data = resp.json()
            usuario = data.get("usuario", {})
            cliente_id = usuario.get("id")
            estado = str(usuario.get("estado", "")).lower()
            activo = estado == "activo"
            if not activo and estado != "active":
                # El servicio actual devuelve el valor de Estado del modelo; se exige usuario activo.
                return Response({"error": "Cuenta no activa"}, status=status.HTTP_403_FORBIDDEN)
        except (ValueError, AttributeError):
            return Response({"error": "Respuesta inválida de Gestión"}, status=status.HTTP_502_BAD_GATEWAY)
        if not data.get("valido") or not cliente_id:
            return Response({"error": "Token inválido"}, status=status.HTTP_401_UNAUTHORIZED)

        order = get_object_or_404(Order, pk=pk, cliente_id=cliente_id)
        return Response(OrderSerializer(order).data)
