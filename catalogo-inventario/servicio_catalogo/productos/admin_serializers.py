from rest_framework import serializers


class CrearProductoSerializer(serializers.Serializer):
    """Datos de entrada para crear un producto (HU-08)."""

    id = serializers.IntegerField(min_value=1)
    nombre = serializers.CharField(max_length=160, allow_blank=False)
    descripcion = serializers.CharField(max_length=2000, allow_blank=False)
    precio = serializers.IntegerField(min_value=1)
    categoria = serializers.CharField(max_length=100, allow_blank=False)
    stock_inicial = serializers.IntegerField(min_value=0)
    imagenes = serializers.ListField(
        child=serializers.URLField(max_length=500),
        min_length=4,
        max_length=6,
        allow_empty=False,
    )
