from django.http import Http404
from rest_framework import generics
from rest_framework.permissions import AllowAny

from usuarios.permissions import EsAdministrador
from .models import Contenido
from .serializers import ContenidoPublicoSerializer, ContenidoSerializer


class ListaCrearContenidoView(generics.ListCreateAPIView):
    serializer_class = ContenidoSerializer
    permission_classes = [EsAdministrador]

    def get_queryset(self):
        queryset = Contenido.objects.all().order_by('pagina', 'orden', 'id')
        pagina = self.request.query_params.get('pagina')
        if pagina:
            queryset = queryset.filter(pagina=pagina)
        return queryset


class DetalleContenidoView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contenido.objects.all()
    serializer_class = ContenidoSerializer
    permission_classes = [EsAdministrador]


class ContenidoPublicoView(generics.ListAPIView):
    serializer_class = ContenidoPublicoSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def get_queryset(self):
        pagina = self.kwargs['pagina']
        if pagina not in Contenido.Pagina.values:
            raise Http404
        return Contenido.objects.filter(
            pagina=pagina, activo=True
        ).order_by('orden', 'id')