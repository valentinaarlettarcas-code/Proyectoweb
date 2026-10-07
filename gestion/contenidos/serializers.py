from rest_framework import serializers
from .models import Contenido


class ContenidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contenido
        fields = [
            'id',
            'titulo',
            'cuerpo',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = [
            'id',
            'fecha_creacion',
            'fecha_actualizacion',
        ]