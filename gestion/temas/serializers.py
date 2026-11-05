from rest_framework import serializers

from .models import Tema


class TemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tema
        fields = ['identificador', 'nombre']


class SeleccionarTemaSerializer(serializers.Serializer):
    tema = serializers.SlugRelatedField(
        slug_field='identificador',
        queryset=Tema.objects.all(),
    )