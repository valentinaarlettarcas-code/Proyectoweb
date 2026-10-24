
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

    
    # Un texto alternativo por imagen.
    textos_alternativos = serializers.ListField(
        child=serializers.CharField(
            max_length=200,
            allow_blank=False,
            trim_whitespace=True,
        ),
        min_length=4,
        max_length=6,
        allow_empty=False,
        required=False,
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)

        imagenes = attrs["imagenes"]
        textos = attrs.get("textos_alternativos")

        if textos is not None and len(textos) != len(imagenes):
            raise serializers.ValidationError({
                "textos_alternativos":
                    "Debe existir un texto alternativo por cada imagen."
            })

        return attrs



# RF17: Edicion administrativa de productos.

class EditarProductoSerializer(serializers.Serializer):
    """Campos permitidos para editar un producto."""

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

    textos_alternativos = serializers.ListField(
        child=serializers.CharField(
            max_length=200,
            allow_blank=False,
            trim_whitespace=True,
        ),
        min_length=4,
        max_length=6,
        allow_empty=False,
        required=False,
    )

    def validate(self, attrs):
        permitidos = {
            "nombre",
            "descripcion",
            "precio",
            "categoria",
            "imagenes",
            "textos_alternativos",
        }

        campos_recibidos = set(self.initial_data.keys())
        campos_invalidos = campos_recibidos - permitidos

        if campos_invalidos:
            raise serializers.ValidationError({
                "campos": (
                    "No se permite modificar: "
                    + ", ".join(sorted(campos_invalidos))
                )
            })

        if not attrs:
            raise serializers.ValidationError(
                "Debes proporcionar al menos un campo para editar."
            )

        tiene_imagenes = "imagenes" in attrs
        tiene_textos = "textos_alternativos" in attrs

        # Las imagenes y sus textos deben actualizarse juntos.
        if tiene_imagenes != tiene_textos:
            raise serializers.ValidationError({
                "imagenes": (
                    "Para actualizar las imagenes debes enviar "
                    "tambien sus textos alternativos, y viceversa."
                )
            })

        if tiene_imagenes:
            if len(attrs["imagenes"]) != len(
                attrs["textos_alternativos"]
            ):
                raise serializers.ValidationError({
                    "textos_alternativos": (
                        "Debe existir un texto alternativo "
                        "por cada imagen."
                    )
                })

        return attrs
