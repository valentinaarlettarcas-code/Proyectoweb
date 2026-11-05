from django.db import models


class Tema(models.Model):
    identificador = models.SlugField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class ConfiguracionSitio(models.Model):
    tema_activo = models.ForeignKey(Tema, on_delete=models.PROTECT)

    @classmethod
    def obtener(cls):
        configuracion, _ = cls.objects.get_or_create(
            pk=1,
            defaults={'tema_activo': Tema.objects.order_by('id').first()},
        )
        return configuracion