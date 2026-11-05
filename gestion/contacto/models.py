from django.db import models


class MensajeContacto(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    mensaje = models.TextField()
    fecha_recepcion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nombre} - {self.fecha_recepcion:%Y-%m-%d %H:%M}'
