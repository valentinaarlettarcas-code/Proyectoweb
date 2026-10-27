from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.permissions import EsAdministrador
from .models import ConfiguracionSitio, Tema
from .serializers import SeleccionarTemaSerializer, TemaSerializer


class ListaTemasView(generics.ListAPIView):
    queryset = Tema.objects.order_by('id')
    serializer_class = TemaSerializer
    permission_classes = [AllowAny]
    authentication_classes = []


class TemaActivoView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        tema = ConfiguracionSitio.obtener().tema_activo
        return Response(TemaSerializer(tema).data)


class SeleccionarTemaView(APIView):
    permission_classes = [EsAdministrador]

    def post(self, request):
        serializer = SeleccionarTemaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tema = serializer.validated_data['tema']
        ConfiguracionSitio.objects.update_or_create(
            pk=1,
            defaults={'tema_activo': tema},
        )
        return Response(TemaSerializer(tema).data)