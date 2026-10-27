# Microservicio de Gestión

Servicio responsable de usuarios, autenticación, roles y estados de cuenta, y también de los contenidos administrables, los temas visuales y los mensajes de contacto.

## Tecnologías

- Django y Django REST Framework
- PostgreSQL
- Token Authentication

## Funcionalidades

- Registro público de clientes, con activación por enlace enviado al correo (token de un solo uso, vigencia de 24 horas).
- Login y logout.
- Autorización por rol y estado.
- Listado y consulta de usuarios para administradores.
- Edición de otros usuarios.
- Bloqueo y desbloqueo de cuentas.
- Protección frente al autobloqueo y del último administrador activo.
- Invalidación del token al cerrar sesión o bloquear una cuenta.
- Contenidos de las páginas públicas, administrables sin cambiar código.
- Temas visuales: consulta del tema activo y selección por el administrador.
- Mensajes de contacto: envío público y consulta por administradores.

## Endpoints principales

Usuarios (`/api/usuarios/`):

- `POST registro/`
- `GET activar/<token>/`
- `POST login/`
- `POST logout/`
- `GET /` (listado)
- `GET <id>/` y `PUT/PATCH <id>/`
- `POST <id>/bloquear/` y `POST <id>/desbloquear/`
- `GET verificar-token/`
- `POST admin/crear/` (solo administrador: crea un usuario pendiente de activación y le envía el token por correo)
- `POST establecer-password/` (público: define la contraseña con el token recibido por correo; un solo uso, vigencia de 24 horas)

Contenidos (`/api/contenidos/`):

- `GET /` y `POST /` (listado y creación)
- `GET publico/<pagina>/` (contenido público de una página)
- `<id>/` (detalle y edición)

Temas (`/api/temas/`):

- `GET /` (lista de temas)
- `GET activo/` (tema vigente)
- `POST seleccionar/` (cambia el tema activo)

Contacto (`/api/contacto/`):

- `POST enviar/` (público)
- `GET mensajes/` y `GET mensajes/<id>/` (administrador)

## Autenticación entre microservicios

Gestión es responsable de validar la identidad, el rol y el estado de los usuarios.

Los demás microservicios no acceden directamente a la base de datos PostgreSQL de Gestión. Para operaciones protegidas, el token recibido se valida mediante la API de Gestión.

El endpoint `/api/usuarios/verificar-token/` devuelve la identidad, rol y estado actual del usuario autenticado. Esto permite rechazar tokens inválidos y evitar que una cuenta bloqueada continúe realizando operaciones autenticadas.

## Roles y estados

- Roles: `CLIENTE`, `ADMIN`.
- Estados: `PENDIENTE`, `ACTIVO`, `BLOQUEADO`.

## Instalación desde un clon limpio

Requisitos: Python con Django 6.1.2 y DRF 3.18.3 (ver `requirements.txt`) y PostgreSQL en ejecución.

1. Entra a la carpeta del servicio y crea un entorno virtual:

        cd gestion
        python -m venv .venv

2. Actívalo. En PowerShell, si la política de ejecución lo impide, usa `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`:

        .\.venv\Scripts\Activate.ps1

3. Instala las dependencias:

        pip install -r requirements.txt

4. Crea la base de datos en PostgreSQL (por defecto `gestion_db`).

5. Define las variables de entorno (ver la sección siguiente).

6. Aplica las migraciones, ejecuta las pruebas y levanta el servidor:

        python manage.py migrate
        python manage.py test
        python manage.py runserver

## Primer administrador

El registro público solo crea clientes. El procedimiento seguro para crear la primera cuenta administradora está en [docs/PRIMER_ADMINISTRADOR.md](../docs/PRIMER_ADMINISTRADOR.md).

## Variables de entorno

La plantilla está en `.env.example`. Django no carga ese archivo por sí solo: las variables deben definirse en la terminal o en la herramienta de despliegue. Nunca se suben valores reales al repositorio.

- `DJANGO_SECRET_KEY` (obligatoria): sin ella el servicio no arranca.
- `DB_PASSWORD` (obligatoria): contraseña del usuario de PostgreSQL.
- `DB_NAME`, `DB_USER`, `DB_HOST`, `DB_PORT` (opcionales): por defecto `gestion_db`, `postgres`, `localhost` y `5432`.
- `EMAIL_BACKEND` (opcional): por defecto los correos de activación se imprimen en la consola del servidor.
- `DJANGO_DEBUG` (opcional): por defecto `True`.
