from rest_framework import generics

from usuarios.permissions import EsAdministrador
from .models import Contenido
from .serializers import ContenidoSerializer


class ListaCrearContenidoView(generics.ListCreateAPIView):
    queryset = Contenido.objects.all().order_by('-fecha_creacion')
    serializer_class = ContenidoSerializer
    permission_classes = [EsAdministrador]


class DetalleContenidoView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contenido.objects.all()
    serializer_class = ContenidoSerializer
    permission_classes = [EsAdministrador]