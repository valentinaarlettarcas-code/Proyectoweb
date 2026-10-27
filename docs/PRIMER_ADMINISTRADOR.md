# Procedimiento seguro del primer administrador

## Objetivo

Crear el primer administrador del servicio de Gestión sin permitir que un usuario público se asigne privilegios administrativos.

## Procedimiento

1. Acceder al servidor o entorno autorizado.
2. Definir las variables de entorno `DJANGO_SECRET_KEY` y `DB_PASSWORD`.
3. Entrar al directorio `gestion` y activar el entorno virtual.
4. Crear el superusuario. El comando pide nombre de usuario, correo y contraseña; usa una contraseña segura y no compartas credenciales:

        python manage.py createsuperuser

5. Asignar el rol de administrador, porque `createsuperuser` deja el rol por defecto (`CLIENTE`). Abre el shell de Django:

        python manage.py shell

   y ejecuta, reemplazando el correo:

        from usuarios.models import Usuario
        u = Usuario.objects.get(email="correo@ejemplo.cl")
        u.rol = "ADMIN"
        u.estado = "ACTIVO"
        u.save()

6. Verificar que el usuario tenga rol `ADMIN`, estado `ACTIVO`, `is_active`, `is_staff` e `is_superuser` en verdadero.

## Seguridad

- El registro público siempre asigna el rol `CLIENTE`.
- No existe un endpoint público para crear administradores.
- Solo personal autorizado puede ejecutar este procedimiento.
- Las credenciales no deben guardarse en Git.
- La creación del primer administrador debe quedar registrada por el equipo responsable.