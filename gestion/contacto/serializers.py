from rest_framework import serializers

from .models import MensajeContacto


class EnviarMensajeSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(min_length=2, max_length=100)
    mensaje = serializers.CharField(min_length=10, max_length=2000)

    class Meta:
        model = MensajeContacto
        fields = ['nombre', 'correo', 'mensaje']


class MensajeContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MensajeContacto
        fields = ['id', 'nombre', 'correo', 'mensaje', 'fecha_recepcion']
        read_only_fields = fields
