from django.db import models


class Contenido(models.Model):
    titulo = models.CharField(max_length=200)
    cuerpo = models.TextField()
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo

