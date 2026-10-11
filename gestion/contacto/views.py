from django.db import DatabaseError
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from usuarios.permissions import EsAdministrador
from .models import MensajeContacto
from .serializers import EnviarMensajeSerializer, MensajeContactoSerializer


class EnviarMensajeView(generics.GenericAPIView):
    serializer_class = EnviarMensajeSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except DatabaseError:
            return Response(
                {'detalle': 'No se pudo registrar el mensaje. Intenta nuevamente.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(
            {'detalle': 'Mensaje recibido correctamente.'},
            status=status.HTTP_201_CREATED,
        )


class ListaMensajesView(generics.ListAPIView):
    queryset = MensajeContacto.objects.all().order_by('-fecha_recepcion')
    serializer_class = MensajeContactoSerializer
    permission_classes = [EsAdministrador]


class DetalleMensajeView(generics.RetrieveAPIView):
    queryset = MensajeContacto.objects.all()
    serializer_class = MensajeContactoSerializer
    permission_classes = [EsAdministrador]
