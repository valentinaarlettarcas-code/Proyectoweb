from django.contrib import admin

from .models import ConfiguracionSitio, Tema

admin.site.register(Tema)
admin.site.register(ConfiguracionSitio)