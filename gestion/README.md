# Microservicio de Gestión

Servicio responsable de usuarios, autenticación, roles y estados de cuenta.

## Tecnologías

- Django
- Django REST Framework
- PostgreSQL
- Token Authentication

## Funcionalidades

- Registro público de clientes.
- Login y logout.
- Autorización por rol y estado.
- Listado y consulta de usuarios para administradores.
- Edición de otros usuarios.
- Bloqueo y desbloqueo de cuentas.
- Protección frente al autobloqueo.
- Protección del último administrador activo.
- Invalidación del token al cerrar sesión o bloquear una cuenta.

## Endpoints principales

- `POST /api/usuarios/registro/`
- `POST /api/usuarios/login/`
- `POST /api/usuarios/logout/`
- `GET /api/usuarios/`
- `GET /api/usuarios/<id>/`
- `PUT/PATCH /api/usuarios/<id>/`
- `POST /api/usuarios/<id>/bloquear/`
- `POST /api/usuarios/<id>/desbloquear/`
- `GET /api/usuarios/verificar-token/`

## Autenticación entre microservicios

Gestión es responsable de validar la identidad, el rol y el estado de los usuarios.

Los demás microservicios no acceden directamente a la base de datos PostgreSQL de Gestión. Para operaciones protegidas, el token recibido se valida mediante la API de Gestión.

El endpoint `/api/usuarios/verificar-token/` devuelve la identidad, rol y estado actual del usuario autenticado.

Esto permite rechazar tokens inválidos y evitar que una cuenta bloqueada continúe realizando operaciones autenticadas.

## Roles

- `CLIENTE`
- `ADMIN`

## Estados

- `PENDIENTE`
- `ACTIVO`
- `BLOQUEADO`

## Base de datos

El servicio utiliza PostgreSQL. La contraseña se obtiene mediante la variable de entorno `DB_PASSWORD` y no se almacena en el repositorio.