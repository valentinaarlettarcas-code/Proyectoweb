
# RF11 - Alta individual de usuarios

## 1. Objetivo

Diseñar un procedimiento seguro para dar de alta usuarios
mediante invitaciones individuales con enlaces de un solo
uso, válidos durante 24 horas.

También se define el procedimiento para crear el primer
administrador del sistema.

Estado: diseño propuesto, pendiente de implementación
y validación con el equipo.

## 2. Actores

- Administrador: genera y gestiona invitaciones.
- Usuario invitado: recibe el enlace y completa el alta.
- Servicio de Gestión: valida invitaciones, usuarios y permisos.

## 3. Flujo de alta individual

1. Un administrador autenticado solicita crear una invitación.
2. Introduce el correo electrónico del nuevo usuario.
3. El sistema comprueba que la operación está autorizada.
4. El servidor genera un token aleatorio criptográficamente seguro.
5. Se almacena únicamente un hash del token.
6. Se registra la fecha de caducidad: creación + 24 horas.
7. Se envía al correo del destinatario un enlace HTTPS.
8. El usuario abre el enlace y accede al formulario de alta.
9. Introduce nombre, apellido y contraseña.
10. El servidor valida el token, su caducidad y su uso previo.
11. Se crea o activa la cuenta correspondiente.
12. El token se marca como utilizado en la misma transacción.
13. Se muestra una confirmación del alta.

El enlace no puede reutilizarse después de completar
correctamente el registro.

## 4. Datos de la invitación

| Campo | Descripción |
| --- | --- |
| id | Identificador de invitación |
| email | Correo del destinatario |
| token_hash | Hash del token generado |
| creado_en | Fecha de creación |
| expira_en | Fecha de caducidad |
| usado_en | Fecha de utilización o null |
| creado_por | Administrador que invita |
| rol_asignado | Rol autorizado para el nuevo usuario |

El token original nunca debe guardarse en texto plano.

## 5. Reglas de seguridad

- Los enlaces caducan a las 24 horas.
- Cada invitación se utiliza una sola vez.
- Los tokens se generan mediante un generador seguro.
- Las contraseñas se almacenan mediante un hash adecuado.
- El servidor valida los permisos del administrador.
- El usuario no puede modificar su rol desde el formulario.
- Los enlaces deben utilizar HTTPS.
- No se registran tokens completos en logs.
- El uso del token debe ser atómico para evitar duplicaciones.
- Los enlaces inválidos, usados o caducados se rechazan.
- El token queda asociado al correo de la invitación.

## 6. Estados de invitación

PENDIENTE:
La invitación existe, no se ha utilizado y sigue vigente.

UTILIZADA:
El usuario completó el alta correctamente.

CADUCADA:
Han transcurrido más de 24 horas desde su creación.

REVOCADA:
Un administrador ha invalidado la invitación.

## 7. Casos de error

| Situación | Resultado |
| --- | --- |
| Token inexistente | Rechazar alta |
| Token caducado | Rechazar y solicitar nueva invitación |
| Token ya utilizado | Rechazar reutilización |
| Invitación revocada | Rechazar alta |
| Contraseña no válida | Mostrar error sin consumir invitación |
| Correo ya registrado | Resolver conflicto sin duplicar cuenta |
| Usuario sin permisos | Impedir generación de invitación |
| Dos usos simultáneos | Permitir como máximo un alta |

## 8. Creación segura del primer administrador

El primer administrador no se crea desde el registro público.

Procedimiento propuesto:

1. Desplegar el servicio con la base de datos configurada.
2. Ejecutar las migraciones necesarias.
3. Utilizar un comando administrativo de inicialización.
4. Obtener el correo y la contraseña inicial mediante
   entrada segura o variables protegidas.
5. Comprobar que no existe un administrador inicial.
6. Crear la cuenta con rol ADMIN y contraseña hasheada.
7. Registrar la operación sin mostrar credenciales.
8. Deshabilitar o restringir la ejecución posterior
   del procedimiento de inicialización.
9. Obligar al cambio de contraseña inicial cuando corresponda.
10. Verificar que el administrador puede acceder al sistema.

El comando debe ejecutarse únicamente desde un entorno
administrativo autorizado.

No se deben incluir contraseñas reales en el repositorio.

## 9. Restricciones del primer administrador

- No existe un registro público con rol ADMIN.
- El rol ADMIN se asigna desde el servidor.
- La creación inicial requiere acceso administrativo.
- Deben evitarse administradores iniciales duplicados.
- Las credenciales nunca se escriben en el código.
- Las acciones administrativas deben quedar registradas.

## 10. Criterios de aceptación

CA01: Un administrador autorizado puede crear una invitación.

CA02: La invitación tiene una duración máxima de 24 horas.

CA03: Un enlace utilizado no puede volver a utilizarse.

CA04: Un enlace caducado o revocado no permite registrarse.

CA05: El usuario puede establecer una contraseña válida.

CA06: El rol del usuario no puede modificarse desde el enlace.

CA07: Dos solicitudes simultáneas no crean cuentas duplicadas.

CA08: El primer ADMIN se crea mediante un procedimiento seguro.

CA09: El registro público no permite crear administradores.

CA10: Las credenciales y tokens no se exponen en logs.

## 11. Pruebas propuestas

- Alta con invitación válida.
- Alta con token inexistente.
- Alta con token caducado.
- Reutilización de enlace.
- Revocación de invitación.
- Contraseña inválida.
- Correo duplicado.
- Solicitudes simultáneas.
- Creación inicial de ADMIN.
- Intento de registro público como ADMIN.

## 12. Pendientes

- Acordar el formato de los endpoints con el equipo.
- Implementar el modelo de invitaciones.
- Implementar el envío de correo.
- Crear el comando seguro de inicialización.
- Programar pruebas automatizadas.
- Validar el diseño con los responsables del proyecto.
