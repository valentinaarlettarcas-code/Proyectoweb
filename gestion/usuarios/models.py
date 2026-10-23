from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        CLIENTE = "CLIENTE", "Cliente"
        ADMIN = "ADMIN", "Administrador"

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        ACTIVO = "ACTIVO", "Activo"
        BLOQUEADO = "BLOQUEADO", "Bloqueado"

    email = models.EmailField(unique=True)

    rol = models.CharField(
        max_length=10,
        choices=Rol.choices,
        default=Rol.CLIENTE
    )

    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.ACTIVO
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email