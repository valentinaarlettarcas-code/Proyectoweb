
# Procedimiento seguro del primer administrador

## Objetivo
Crear el primer administrador del servicio de Gestión sin permitir que un usuario público se asigne privilegios administrativos.

## Procedimiento

1. Acceder al servidor o entorno autorizado.
2. Configurar las variables de entorno `DJANGO_SECRET_KEY` y `DB_PASSWORD`.
3. Acceder al directorio `gestion`.
4. Ejecutar:

   .\venv\Scripts\python.exe manage.py createsuperuser

5. Introducir un correo y una contraseña segura, sin compartir credenciales.
6. Verificar que el usuario tenga:
   - rol = ADMIN
   - estado = ACTIVO
   - is_active = True
   - is_staff = True
   - is_superuser = True

## Seguridad

- El registro público siempre asigna el rol CLIENTE.
- No existe un endpoint público para crear administradores.
- Solo personal autorizado puede ejecutar este procedimiento.
- Las credenciales no deben guardarse en Git.
- La creación del primer administrador debe quedar registrada por el equipo responsable.
- Se recomienda habilitar MFA para el panel administrativo cuando esté disponible.
