from django.db import models


class Contenido(models.Model):
    class Pagina(models.TextChoices):
        INICIO = 'inicio', 'Inicio'
        CONTACTO = 'contacto', 'Contacto'
        QUIENES_SOMOS = 'quienes-somos', 'Quiénes somos'

    class Tipo(models.TextChoices):
        TEXTO = 'texto', 'Texto'
        IMAGEN = 'imagen', 'Imagen'
        ENLACE = 'enlace', 'Enlace'
        BANNER = 'banner', 'Banner'

    pagina = models.CharField(
        max_length=20, choices=Pagina.choices, default=Pagina.INICIO
    )
    clave = models.SlugField(max_length=50, default='bloque')
    tipo = models.CharField(
        max_length=10, choices=Tipo.choices, default=Tipo.TEXTO
    )
    titulo = models.CharField(max_length=200, blank=True)
    cuerpo = models.TextField(blank=True)
    imagen_url = models.CharField(max_length=500, blank=True)
    texto_alternativo = models.CharField(max_length=200, blank=True)
    enlace_url = models.CharField(max_length=500, blank=True)
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['pagina', 'orden', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['pagina', 'clave'],
                name='contenido_clave_unica_por_pagina',
            ),
        ]

    def __str__(self):
        return f'{self.pagina}/{self.clave}'