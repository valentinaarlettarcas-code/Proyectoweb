from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import URLValidator
from rest_framework import serializers

from .models import Contenido

_validador_url = URLValidator(schemes=['http', 'https'])

CAMPOS_OBLIGATORIOS = {
    'texto': ['cuerpo'],
    'imagen': ['imagen_url', 'texto_alternativo'],
    'enlace': ['titulo', 'enlace_url'],
    'banner': ['titulo', 'imagen_url', 'texto_alternativo'],
}


def _url_o_ruta(valor):
    valor = valor.strip()
    if not valor:
        return valor
    if valor.startswith('/') and not valor.startswith('//'):
        return valor
    try:
        _validador_url(valor)
    except DjangoValidationError:
        raise serializers.ValidationError(
            'Debe ser una URL http(s) válida o una ruta interna que empiece con "/".'
        )
    return valor


class ContenidoSerializer(serializers.ModelSerializer):
    pagina = serializers.ChoiceField(choices=Contenido.Pagina.choices)
    clave = serializers.SlugField(max_length=50)
    tipo = serializers.ChoiceField(choices=Contenido.Tipo.choices)
    titulo = serializers.CharField(
        max_length=200, required=False, allow_blank=True
    )
    cuerpo = serializers.CharField(
        max_length=2000, required=False, allow_blank=True
    )
    texto_alternativo = serializers.CharField(
        max_length=200, required=False, allow_blank=True
    )

    class Meta:
        model = Contenido
        fields = [
            'id', 'pagina', 'clave', 'tipo', 'titulo', 'cuerpo',
            'imagen_url', 'texto_alternativo', 'enlace_url', 'orden',
            'activo', 'fecha_creacion', 'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

    def validate_imagen_url(self, valor):
        return _url_o_ruta(valor)

    def validate_enlace_url(self, valor):
        return _url_o_ruta(valor)

    def validate(self, datos):
        def valor(campo):
            if campo in datos:
                return datos[campo] or ''
            if self.instance is not None:
                return getattr(self.instance, campo) or ''
            return ''

        obligatorios = CAMPOS_OBLIGATORIOS.get(valor('tipo'), [])
        errores = {
            campo: 'Este campo es obligatorio para este tipo de contenido.'
            for campo in obligatorios
            if not str(valor(campo)).strip()
        }
        if errores:
            raise serializers.ValidationError(errores)
        return datos


class ContenidoPublicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contenido
        fields = [
            'pagina', 'clave', 'tipo', 'titulo', 'cuerpo',
            'imagen_url', 'texto_alternativo', 'enlace_url', 'orden',
        ]
        read_only_fields = fields