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


## 16. Endpoints adicionales de Gestión

Actualización: 16/11/2026.

Las siguientes rutas, métodos y permisos se han
contrastado con urls.py y views.py del servicio Gestión.

| Método | Endpoint | Acceso |
|---|---|---|
| GET | /api/usuarios/activar/{token}/ | Público |
| POST | /api/usuarios/admin/crear/ | ADMIN activo |
| POST | /api/usuarios/establecer-password/ | Público |
| GET, POST | /api/contenidos/ | ADMIN activo |
| GET, PUT, PATCH, DELETE | /api/contenidos/{id}/ | ADMIN activo |
| GET | /api/contenidos/publico/{pagina}/ | Público |
| GET | /api/temas/ | Público |
| GET | /api/temas/activo/ | Público |
| POST | /api/temas/seleccionar/ | ADMIN activo |
| POST | /api/contacto/enviar/ | Público |
| GET | /api/contacto/mensajes/ | ADMIN activo |
| GET | /api/contacto/mensajes/{id}/ | ADMIN activo |

### 16.1. Permisos

Los endpoints administrativos utilizan EsAdministrador.

Los endpoints públicos utilizan AllowAny.

Los endpoints públicos de contenidos, temas y contacto
deshabilitan explícitamente la autenticación mediante
authentication_classes = [].

EstablecerPasswordView también deshabilita la autenticación.

### 16.2. Importación CSV

La importación CSV forma parte del alcance de Gestión,
pero no aparece declarada en el archivo usuarios/urls.py
de la rama actual.

Debe revisarse la rama feature/scrum-27-importacion-csv
antes de incorporar una ruta al contrato.

### 16.3. Verificación pendiente

Falta contrastar los campos de entrada, las respuestas
JSON y los códigos de error de estas funcionalidades
con los serializers y la implementación de las vistas.

No se considera finalizada la validación del contrato
hasta completar esa revisión.

### 16.4. Gestión de contacto

| Ruta | Vista | Función |
|---|---|---|
| /api/contacto/enviar/ | EnviarMensajeView | Enviar mensaje |
| /api/contacto/mensajes/ | ListaMensajesView | Listar mensajes |
| /api/contacto/mensajes/{id}/ | DetalleMensajeView | Consultar mensaje |

### 16.5. Importación CSV

La importación masiva de usuarios pertenece al alcance de
Gestión, pero no aparece entre las rutas del archivo
gestion/usuarios/urls.py revisado.

Pendiente de confirmar si está integrada en otra vista,
rama o configuración antes de documentar su endpoint.

### 16.6. Estado de verificación

- Rutas y nombres de vistas: contrastados con urls.py.
- Métodos HTTP: pendientes de contrastar con views.py.
- Permisos: pendientes de contrastar con las vistas.
- Campos y respuestas JSON: pendientes de contrastar.
- Pruebas: existe una ejecución de 19 tests correctos,
  pero no se ha confirmado que cubran todos estos endpoints.


## 17. Activación y creación administrativa de usuarios

### 17.1. Activación de cuentas

GET /api/usuarios/activar/{token}/

Acceso: público.

Permite activar una cuenta que se encuentra en estado PENDIENTE.

El token:
- Se valida mediante SHA-256.
- Caduca a las 24 horas.
- Solo puede utilizarse una vez.

Respuesta HTTP 200:

```json
{
  "mensaje": "Cuenta activada correctamente."
}
```

Errores HTTP 400:
- Enlace no válido.
- Enlace utilizado anteriormente.
- Enlace caducado.
- Cuenta que no está pendiente de activación.

Al completar la operación, el usuario pasa a estado ACTIVO.


### 17.2. Creación administrativa de usuarios

**Endpoint:** POST /api/usuarios/admin/crear/

**Permiso:** ADMIN activo.

Permite al administrador crear usuarios con un rol asignado.

Solicitud JSON:

```json
{
  "first_name": "Ana",
  "last_name": "Pérez",
  "email": "ana@example.com",
  "rol": "CLIENTE"
}
```

Validaciones:
- Nombre y apellido obligatorios y no vacíos.
- Correo electrónico válido y no duplicado.
- Rol perteneciente a los valores definidos por Usuario.Rol.
- El correo se normaliza a minúsculas.
- El usuario se crea en estado PENDIENTE.
- La cuenta queda inicialmente desactivada.
- Se establece una contraseña no utilizable.

El servidor genera un token de configuración y envía
un correo electrónico al usuario.

El token caduca a las 24 horas y es de un solo uso.

Respuesta HTTP 201:

```json
{
  "mensaje": "Usuario creado. Se ha enviado el token de configuración.",
  "id": 12
}
```

Errores:
- HTTP 400: datos inválidos o correo duplicado.
- Acceso denegado si no se cumplen los permisos de administrador.

### 17.3. Establecimiento de contraseña

**Endpoint:** POST /api/usuarios/establecer-password/

**Permiso:** Público.

Permite configurar la contraseña de una cuenta pendiente
utilizando un token de configuración válido.

Solicitud JSON:

```json
{
  "token": "TOKEN_RECIBIDO_POR_CORREO",
  "password": "ClaveSegura123!",
  "confirmar_password": "ClaveSegura123!"
}
```

Validaciones:
- Los tres campos son obligatorios.
- La contraseña debe tener al menos ocho caracteres.
- password y confirmar_password deben coincidir.
- El token debe existir.
- El token no debe haber sido utilizado.
- El token debe tener menos de 24 horas.
- La cuenta debe encontrarse en estado PENDIENTE.
- El usuario no debe tener una contraseña utilizable.
- La contraseña debe superar los validadores de Django.

Cuando la operación es correcta:
1. Se almacena la contraseña mediante set_password().
2. La cuenta pasa a estado ACTIVO.
3. Se establece is_active = True.
4. El token queda marcado como utilizado.

Respuesta HTTP 200:

```json
{
  "mensaje": "Contraseña configurada y cuenta activada."
}
```

Errores HTTP 400:
- Token inválido.
- Token utilizado anteriormente.
- Token caducado.
- Cuenta no pendiente.
- Cuenta que ya tiene una contraseña.
- Contraseñas que no coinciden.
- Contraseña que no supera las validaciones.

Los errores de validación de contraseña se devuelven
en el campo "password".

Las contraseñas nunca se incluyen en las respuestas.


## 18. Gestión de contenidos

### 18.1. Listar y crear contenidos

**Endpoint:** /api/contenidos/

**Permiso:** ADMIN activo.

- GET: devuelve la lista de contenidos.
- POST: permite crear un contenido.

La lista se ordena por pagina, orden e id.

Se admite el parámetro opcional de consulta:

GET /api/contenidos/?pagina=inicio

Este parámetro filtra los contenidos por página.

Respuestas estándar de Django REST Framework:
- GET: HTTP 200.
- POST: HTTP 201 cuando se crea correctamente.
- HTTP 400 cuando falla la validación.

### 18.2. Gestionar un contenido individual

**Endpoint:** /api/contenidos/{id}/

**Permiso:** ADMIN activo.

- GET: consultar un contenido.
- PUT: reemplazar los campos editables.
- PATCH: actualizar parcialmente.
- DELETE: eliminar el contenido.

Respuestas estándar:
- GET, PUT y PATCH correctos: HTTP 200.
- DELETE correcto: HTTP 204.
- Contenido inexistente: HTTP 404.

### 18.3. Contenidos públicos

**Endpoint:** GET /api/contenidos/publico/{pagina}/

**Permiso:** Público.

Devuelve únicamente los contenidos de la página indicada
cuyo atributo activo sea True.

Los resultados se ordenan por orden e id.

Si la página no pertenece a los valores definidos
en Contenido.Pagina, devuelve HTTP 404.

La estructura JSON exacta depende de
ContenidoPublicoSerializer.

---

## 19. Gestión de temas

### 19.1. Consultar temas

**Endpoint:** GET /api/temas/

**Permiso:** Público.

Devuelve los temas disponibles, ordenados por id.

Respuesta correcta: HTTP 200.

### 19.2. Consultar tema activo

**Endpoint:** GET /api/temas/activo/

**Permiso:** Público.

Devuelve la configuración del tema actualmente seleccionado.

La respuesta utiliza TemaSerializer.

Respuesta correcta: HTTP 200.

### 19.3. Seleccionar tema

**Endpoint:** POST /api/temas/seleccionar/

**Permiso:** ADMIN activo.

Permite seleccionar un tema mediante
SeleccionarTemaSerializer.

El servidor actualiza o crea la configuración
de sitio con pk=1.

Respuesta correcta: HTTP 200.

La respuesta utiliza TemaSerializer.

Los campos exactos de entrada y salida deben
contrastarse con los serializers.

---

## 20. Gestión de contacto

### 20.1. Enviar un mensaje

**Endpoint:** POST /api/contacto/enviar/

**Permiso:** Público.

Permite enviar un mensaje mediante
EnviarMensajeSerializer.

Respuesta HTTP 201:

{
  "detalle": "Mensaje recibido correctamente."
}

Si ocurre un error de base de datos al guardar
el mensaje, devuelve HTTP 503:

{
  "detalle": "No se pudo registrar el mensaje. Intenta nuevamente."
}

Los errores de validación devuelven HTTP 400
con el formato de Django REST Framework.

### 20.2. Listar mensajes

**Endpoint:** GET /api/contacto/mensajes/

**Permiso:** ADMIN activo.

Devuelve los mensajes recibidos ordenados por
fecha_recepcion descendente e id descendente.

Utiliza MensajeContactoSerializer.

Respuesta correcta: HTTP 200.

### 20.3. Consultar mensaje individual

**Endpoint:** GET /api/contacto/mensajes/{id}/

**Permiso:** ADMIN activo.

Devuelve el mensaje identificado por su id.

Respuesta correcta: HTTP 200.

Si el mensaje no existe, devuelve HTTP 404.

---

## 21. Estado de validación

Las rutas, métodos y permisos de contenidos,
temas y contacto se han contrastado con la
implementación de Django REST Framework.

Pendiente:
- Documentar los campos exactos de los serializers.
- Confirmar la integración de importación CSV.
- Revisar la documentación de RF11.
- Revisar los wireframes.
- Validar las respuestas mediante pruebas.
- Obtener aprobación del Pull Request.
