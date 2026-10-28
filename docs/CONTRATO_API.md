# Contrato de API - Servicio de Gestion

## 1. Objetivo y estado

Proyecto: E-commerce de accesorios tech y gaming.

Este contrato documenta la API de Gestion de usuarios, autenticacion, roles y estados.

Referencia: codigo de la rama feature/gestion-usuarios-auth revisado el 19/10/2026.

Estado: documentacion contrastada con el codigo fuente. Pendiente de pruebas de integracion y aprobacion del equipo.

## 2. Convenciones

- URL base: /api/usuarios/
- Formato: JSON.
- Framework: Django REST Framework.
- Autenticacion: DRF TokenAuthentication.
- Cabecera: Authorization: Token <token>
- No se utilizan JWT ni tokens Bearer.
- No se ha configurado caducidad automatica del token.
- El login invalida los tokens anteriores y genera uno nuevo.
- Las contrasenas nunca se devuelven.
- HTTPS es obligatorio en despliegues reales.

Los ejemplos son ilustrativos. Los identificadores y datos dependen de la base de datos.

## 3. Endpoints existentes

| Metodo | Ruta | Funcion | Acceso |
| --- | --- | --- | --- |
| POST | /api/usuarios/registro/ | Registrar cliente | Publico previsto |
| POST | /api/usuarios/login/ | Iniciar sesion | Publico previsto |
| POST | /api/usuarios/logout/ | Cerrar sesion | Autenticado |
| GET | /api/usuarios/ | Listar usuarios | ADMIN activo |
| GET | /api/usuarios/{id}/ | Consultar usuario | ADMIN activo |
| PUT/PATCH | /api/usuarios/{id}/ | Actualizar usuario | ADMIN activo |
| POST | /api/usuarios/{id}/bloquear/ | Bloquear usuario | ADMIN activo |
| POST | /api/usuarios/{id}/desbloquear/ | Desbloquear usuario | ADMIN activo |
| GET | /api/usuarios/verificar-token/ | Verificar token autenticado | Autenticado |

Los metodos se deducen de las vistas DRF implementadas. Los permisos publicos deben confirmarse tambien con la configuracion final de permisos globales.

No existen en las rutas revisadas los endpoints /usuarios/me/ propuestos anteriormente.

## 4. Registro

POST /api/usuarios/registro/

Solicitud:

```json
{
  "first_name": "Ana",
  "last_name": "Perez",
  "email": "ana@example.com",
  "password": "ClaveSegura123!"
}
```

Respuesta implementada: HTTP 201.

```json
{
  "mensaje": "Cliente registrado correctamente.",
  "usuario": {
    "id": 12,
    "nombre": "Ana",
    "apellido": "Perez",
    "email": "ana@example.com",
    "rol": "CLIENTE",
    "estado": "ACTIVO"
  }
}
```

Reglas observadas:

- El servidor asigna siempre CLIENTE y ACTIVO.
- El rol ADMIN enviado por el cliente no forma parte de los campos admitidos.
- El correo se normaliza y se comprueba que no este duplicado.
- La contrasena se almacena mediante set_password().
- El serializer exige al menos ocho caracteres.
- Los validadores completos de Django aun no se invocan expresamente en el serializer.
- Debe reforzarse la obligatoriedad de nombre y apellido.

## 5. Inicio de sesion

POST /api/usuarios/login/

Solicitud:

```json
{
  "email": "ana@example.com",
  "password": "ClaveSegura123!"
}
```

Respuesta implementada: HTTP 200.

```json
{
  "mensaje": "Inicio de sesión correcto.",
  "token": "<token>",
  "usuario": {
    "id": 12,
    "nombre": "Ana",
    "apellido": "Perez",
    "email": "ana@example.com",
    "rol": "CLIENTE",
    "estado": "ACTIVO"
  }
}
```

Solo pueden iniciar sesion las cuentas activas con credenciales correctas.

El token anterior del usuario se elimina y se crea otro.

No se devuelven access_token, token_type ni expires_in.

## 6. Cierre de sesion

POST /api/usuarios/logout/

Requiere:

Authorization: Token <token>

Respuesta implementada: HTTP 200.

```json
{
  "mensaje": "Sesión cerrada correctamente."
}
```

El servidor elimina el token del usuario autenticado.

## 7. Administracion de usuarios

GET /api/usuarios/

Lista usuarios mediante UsuarioSerializer, con acceso reservado a ADMIN activo.

GET /api/usuarios/{id}/

Consulta el detalle del usuario indicado.

PUT /api/usuarios/{id}/

PATCH /api/usuarios/{id}/

Actualizan campos permitidos por UsuarioSerializer.

Campos expuestos por el serializer:

- id
- first_name
- last_name
- email
- rol
- estado
- fecha_creacion
- fecha_actualizacion

id, rol, estado y las fechas son de solo lectura.

El administrador no puede editar su propia cuenta mediante DetalleUsuarioView.

El email y el username se mantienen sincronizados al actualizar.

## 8. Bloqueo de usuarios

POST /api/usuarios/{id}/bloquear/

Requiere ADMIN activo.

Respuesta correcta: HTTP 200.

```json
{
  "mensaje": "Usuario bloqueado correctamente."
}
```

El administrador no puede bloquear su propia cuenta.

Si el usuario afectado es el ultimo administrador activo, el backend intenta impedir su bloqueo.

Al bloquear, se eliminan sus tokens.

Pendiente para Sprint 3: proteger correctamente la comprobacion del ultimo administrador mediante transaction.atomic(), select_for_update() y test de concurrencia.

## 9. Desbloqueo de usuarios

POST /api/usuarios/{id}/desbloquear/

Requiere ADMIN activo.

Respuesta actual: HTTP 200.

```json
{
  "mensaje": "Usuario desbloqueado correctamente."
}
```

El backend actual asigna el estado ACTIVO.

Pendiente para Sprint 3: rechazar la operacion cuando la cuenta no se encuentre previamente en estado BLOQUEADO e incorporar un test.

## 10. Verificacion de token

GET /api/usuarios/verificar-token/

Cabecera requerida:

Authorization: Token <token>

No recibe un token en un cuerpo JSON.

El servidor utiliza request.user, obtenido por TokenAuthentication.

Respuesta implementada para usuario ACTIVO: HTTP 200.

```json
{
  "valido": true,
  "usuario": {
    "id": 12,
    "email": "ana@example.com",
    "rol": "CLIENTE",
    "estado": "ACTIVO"
  }
}
```

Respuesta implementada cuando se alcanza la vista con un usuario no activo: HTTP 403.

```json
{
  "valido": false,
  "error": "Usuario no activo."
}
```

Cuando falta el token o es invalido, DRF puede rechazar la peticion antes de ejecutar la vista. El formato concreto de ese error no coincide necesariamente con el ejemplo anterior y debe comprobarse mediante pruebas.

Contrato interno entre servicios:

- El formato anterior refleja el backend actual.
- Todavia no existe una autenticacion independiente de servicios consumidores.
- No se debe exponer el token de usuario a servicios no confiables.
- Catalogo y Comercio deben confirmar el mecanismo de integracion.
- Debe acordarse un contrato definitivo antes de dar por cerrada la integracion entre servicios.

## 11. Permisos

EsAdministrador exige:

- Usuario autenticado.
- Estado ACTIVO.
- Rol ADMIN.

EsCliente exige:

- Usuario autenticado.
- Estado ACTIVO.
- Rol CLIENTE.

EsUsuarioActivo exige:

- Usuario autenticado.
- Estado ACTIVO.

Las tres clases estan definidas, pero solo se consideran aplicadas donde las vistas efectivamente las configuran.

Logout y verificar-token utilizan IsAuthenticated.

## 12. Errores

Ejemplos confirmados por las vistas:

- HTTP 403: no puedes editar tu propio usuario.
- HTTP 403: no puedes bloquear tu propia cuenta.
- HTTP 400: intento de bloquear al ultimo administrador activo.
- HTTP 404: usuario no encontrado al bloquear o desbloquear.
- HTTP 403: usuario no activo en verificar-token, cuando se ejecuta dicha comprobacion.

Los errores de validacion de serializers utilizan las estructuras de error de Django REST Framework.

No hay un formato JSON universal de error personalizado implementado en todas las vistas.

Los codigos 409 y 429 propuestos anteriormente no estan confirmados por la implementacion revisada.

Las respuestas reales deben verificarse con tests antes de establecer un contrato definitivo de errores.

## 13. Seguridad

- No almacenar contrasenas en texto plano.
- Utilizar HTTPS en produccion.
- No registrar tokens ni credenciales en logs.
- Proteger las funciones administrativas en el servidor.
- No confiar en el rol enviado durante el registro.
- No compartir secretos mediante Git.
- Configurar DB_PASSWORD mediante una variable de entorno.
- Aplicar las correcciones de concurrencia y validacion pendientes.

## 14. Integracion con otros servicios

Los servicios de Catalogo y Comercio necesitan consultar identidad, rol y estado de usuarios.

Actualmente existe GET /api/usuarios/verificar-token/ con TokenAuthentication.

Antes de utilizarlo como contrato definitivo entre microservicios, el equipo debe acordar:

1. Como se autenticara cada servicio consumidor.
2. Como se transmitira el token de forma segura.
3. El formato definitivo de respuestas correctas y errores.
4. El comportamiento cuando Gestion no este disponible.
5. La comprobacion de permisos y estados requerida por cada servicio.

Ante un error de verificacion, el consumidor no debe conceder autorizacion por defecto.

## 15. Pendientes y criterios de cierre

- Ejecutar pruebas reales de endpoints.
- Acordar verificar-token con los equipos consumidores.
- Confirmar permisos globales y publicos.
- Documentar codigos de error mediante respuestas probadas.
- Incorporar tests de seguridad de rol y estado.
- Implementar los ajustes del Sprint 3.
- Obtener revision y aprobacion del Pull Request.

Esta documentacion describe la implementacion observada, pero no certifica por si sola el correcto funcionamiento del backend.
