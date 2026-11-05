from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/usuarios/', include('usuarios.urls')),
    path('api/contenidos/', include('contenidos.urls')),
]
urlpatterns += [path('api/contacto/', include('contacto.urls'))]
urlpatterns += [path('api/temas/', include('temas.urls'))]
