# Investigación de despliegue — Solemne 02

**Responsabilidad:** Escuadrón 3 — Servicio Comercio  
**Alcance:** alojamiento, HTTPS, cuotas, CORS, persistencia, bases de datos y recepción de webhooks.

## 1. Resumen ejecutivo

Se compararon alternativas para desplegar el frontend React + Vite, servicios Django REST Framework y bases de datos. Como punto de partida se propone evaluar:

- **Frontend:** Vercel Hobby o Render Static Site.
- **Servicios Django/DRF:** Render Web Services, uno por servicio si la arquitectura del equipo los separa.
- **MongoDB:** MongoDB Atlas, previa verificación de compatibilidad con las operaciones atómicas/transacciones que requiera el diseño.
- **PostgreSQL:** un servicio administrado compatible. No se recomienda depender de Render PostgreSQL gratuito para todo el semestre porque vence a los 30 días.

Esta es una recomendación preliminar para un proyecto académico. La elección final requiere una prueba de despliegue y un acuerdo del equipo sobre costos, cuotas y duración de los datos.

## 2. Comparación de proveedores

| Componente | Alternativa | Ventajas | Riesgos o límites a revisar |
|---|---|---|---|
| Frontend React + Vite | Vercel Hobby | Integración con Git, despliegues de frontend y HTTPS automático. | Revisar límites del plan y configurar correctamente rutas SPA y URL de API. |
| Frontend estático | Render Static Site | Opción gratuita para servir archivos estáticos. | Revisar cuotas compartidas de ancho de banda y minutos de compilación. |
| APIs Django/DRF | Render Web Services | Despliegue independiente de servicios Python y HTTPS gestionado. | Los servicios gratuitos se suspenden tras 15 minutos sin tráfico y pueden tardar alrededor de un minuto en despertar. |
| PostgreSQL | Base administrada | Adecuada para usuarios/gestión y órdenes/comercio según la arquitectura acordada. | Confirmar precio, backups, límite de almacenamiento, conexiones y vigencia de la cuota gratuita. |
| MongoDB | MongoDB Atlas | Servicio administrado con clúster gratuito para desarrollo pequeño. | El clúster gratuito tiene límites; verificar las operaciones/transacciones necesarias y la capacidad disponible. |

## 3. HTTPS y configuración segura

- El frontend, las API y el endpoint de webhook deben utilizar HTTPS en el entorno publicado.
- Guardar `SECRET_KEY`, contraseñas y cadenas de conexión como variables de entorno del proveedor; nunca subir secretos al repositorio.
- Para Django en despliegue: configurar `DEBUG = False`, `ALLOWED_HOSTS` con los dominios correctos y los ajustes de cookies/CSRF que correspondan.
- Ejecutar `python manage.py check --deploy` antes de publicar.
- Validar las notificaciones del proveedor de pagos en el servidor mediante el mecanismo de autenticación/firma que indique el proveedor.
- Mantener los pagos en sandbox según la evaluación.
- Revisar logs y probar la recuperación cuando un servicio esté temporalmente caído.

Fuente oficial de Django: https://docs.djangoproject.com/en/6.0/howto/deployment/

## 4. CORS

Si el frontend y las APIs tienen dominios diferentes, Django debe permitir el origen real del frontend.

- Usar `CORS_ALLOWED_ORIGINS` con orígenes explícitos, por ejemplo `https://nombre-proyecto.vercel.app`.
- No permitir todos los orígenes de forma indiscriminada.
- Revisar que el middleware de `django-cors-headers` esté instalado y ubicado según su documentación.
- CORS no reemplaza la autenticación ni la autorización.
- Si se utilizan cookies/sesiones entre dominios, revisar además CSRF y la configuración de credenciales.

Documentación: https://github.com/adamchainz/django-cors-headers

## 5. Cuotas y persistencia

### Render gratuito

La documentación oficial indica que los servicios web gratuitos se apagan tras 15 minutos sin tráfico entrante; al recibir una nueva solicitud pueden tardar cerca de un minuto en arrancar. El sistema de archivos es efímero, por lo que no se deben guardar allí datos que deban persistir. Render PostgreSQL gratuito tiene 1 GB, expira a los 30 días y no incluye backups ni connection pooling administrado.

**Conclusión:** útil para pruebas o demostraciones cortas, pero no debe seleccionarse como base PostgreSQL estable para todo el semestre sin un plan de migración/upgrade y respaldo.

Fuente: https://render.com/docs/free

### Vercel Hobby

El plan Hobby es gratuito y ofrece integración con Git, despliegues de frontend y HTTPS/SSL automático. Tiene límites de uso que deben revisarse para el tamaño del proyecto. Para una SPA React + Vite, comprobar que las rutas internas sigan funcionando al recargar una URL; si hace falta, configurar una regla de rewrite.

Fuentes:
- https://vercel.com/docs/plans
- https://vercel.com/docs/limits
- https://vercel.com/docs/frameworks/frontend/vite

### MongoDB Atlas Free

Atlas Free permite un clúster pequeño con replicación de tres nodos, pero tiene almacenamiento y funciones limitadas y no permite activar backups administrados. El equipo debe verificar que el tipo de clúster elegido sea compatible con las transacciones y operaciones atómicas que el diseño de inventario requiera. No asumir que una función está disponible sin comprobarlo.

Fuentes:
- https://www.mongodb.com/docs/atlas/reference/free-shared-limitations/
- https://www.mongodb.com/docs/atlas/reference/atlas-limits/

## 6. Requisitos específicos de Comercio y pagos

- El proveedor de pagos debe tener un sandbox y documentar el uso de moneda y pruebas que necesita el equipo.
- Debe existir una URL pública HTTPS para recibir webhooks.
- El backend debe verificar la notificación con el mecanismo oficial del proveedor; no confiar solamente en una redirección del navegador.
- Procesar eventos de forma idempotente: recibir dos veces un evento no debe duplicar cambios.
- La orden solo queda `CONFIRMADA` cuando el pago está verificado y el inventario está consolidado.
- Si la respuesta de inventario no llega o es contradictoria, mantener la orden pendiente o enviarla a revisión/conciliación; no asumir éxito.
- Guardar datos sensibles solo cuando sean necesarios y nunca registrar claves secretas en logs.

## 7. Lista de verificación para decidir y probar

- [ ] Cada servicio puede desplegarse de forma independiente.
- [ ] El frontend puede comunicarse con cada API usando HTTPS.
- [ ] CORS permite el origen correcto y bloquea los no autorizados.
- [ ] Las variables de entorno y secretos no están en Git.
- [ ] PostgreSQL tiene una solución que cubre toda la duración de la evaluación.
- [ ] MongoDB soporta las transacciones/operaciones requeridas por inventario.
- [ ] El almacenamiento persistente no depende del disco efímero del servicio web.
- [ ] El webhook puede recibir notificaciones externas en una URL pública HTTPS.
- [ ] El proveedor de pago sandbox y la moneda requerida por el equipo están verificados.
- [ ] Se prueban reintentos, duplicados y caída temporal de servicios.
- [ ] Se conocen las cuotas de almacenamiento, transferencia, compilación y conexiones.
- [ ] Se ejecuta `python manage.py check --deploy` antes de publicar.

## 8. Recomendación final provisional

Para el frontend, evaluar Vercel Hobby por su integración Git y HTTPS automático. Para Django/DRF, Render puede facilitar una demostración, teniendo en cuenta el arranque en frío y el sistema de archivos efímero. Para MongoDB, evaluar Atlas Free después de comprobar la compatibilidad de transacciones. Para PostgreSQL, no depender de Render gratuito durante todo el semestre porque vence a los 30 días; comparar una alternativa administrada que cubra el período de la evaluación o definir una migración respaldada.

**La decisión final queda pendiente de una prueba real y de la aprobación del equipo.** No se han creado cuentas, bases de datos ni servicios de despliegue en nombre del equipo.

## 9. Fuentes oficiales consultadas

1. Django — Deployment checklist: https://docs.djangoproject.com/en/6.0/howto/deployment/
2. Render — Free services and databases: https://render.com/docs/free
3. Vercel — Plans: https://vercel.com/docs/plans
4. Vercel — Limits: https://vercel.com/docs/limits
5. Vercel — Vite: https://vercel.com/docs/frameworks/frontend/vite
6. MongoDB Atlas — Free cluster limitations: https://www.mongodb.com/docs/atlas/reference/free-shared-limitations/
7. MongoDB Atlas — Service limits: https://www.mongodb.com/docs/atlas/reference/atlas-limits/
8. django-cors-headers — Configuration: https://github.com/adamchainz/django-cors-headers
