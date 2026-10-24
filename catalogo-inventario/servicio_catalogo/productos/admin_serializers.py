
from rest_framework import serializers


# HU-08: Creacion administrativa de productos.
class CrearProductoSerializer(serializers.Serializer):
    """Datos de entrada para crear un producto."""

    id = serializers.IntegerField(min_value=1)

    nombre = serializers.CharField(
        max_length=160,
        allow_blank=False,
    )

    descripcion = serializers.CharField(
        max_length=2000,
        allow_blank=False,
    )

    precio = serializers.IntegerField(min_value=1)

    categoria = serializers.CharField(
        max_length=100,
        allow_blank=False,
    )

    stock_inicial = serializers.IntegerField(min_value=0)

    imagenes = serializers.ListField(
        child=serializers.URLField(max_length=500),
        min_length=4,
        max_length=6,
        allow_empty=False,
    )


# RF17: Edicion administrativa de productos.
class EditarProductoSerializer(serializers.Serializer):
    """
    Permite editar los datos comerciales del producto.

    No permite modificar el identificador, el inventario
    ni el estado de activacion del producto.
    """

    nombre = serializers.CharField(
        max_length=160,
        allow_blank=False,
        required=False,
    )

    descripcion = serializers.CharField(
        max_length=2000,
        allow_blank=False,
        required=False,
    )

    precio = serializers.IntegerField(
        min_value=1,
        required=False,
    )

    categoria = serializers.CharField(
        max_length=100,
        allow_blank=False,
        required=False,
    )

    imagenes = serializers.ListField(
        child=serializers.URLField(max_length=500),
        min_length=4,
        max_length=6,
        allow_empty=False,
        required=False,
    )

    def validate(self, attrs):
        """
        Rechaza campos no permitidos y solicitudes vacias.
        """

        campos_no_permitidos = sorted(
            set(self.initial_data) - set(self.fields)
        )

        if campos_no_permitidos:
            raise serializers.ValidationError({
                "campos_no_permitidos": campos_no_permitidos
            })

        if not attrs:
            raise serializers.ValidationError(
                "Debes enviar al menos un campo editable."
            )

        return attrs
