# Checklist de entregables — Arquitectura e integración

Marcar cada punto solo cuando esté comprobado.

- [ ] Diagrama con Frontend, Gestión, Comercio, Catálogo/Inventario y bases de datos.
- [ ] Identificar qué datos pertenece a cada servicio.
- [ ] Documentar llamadas entre servicios y respuestas.
- [ ] Validar autenticación de Gestión y autenticación interna del catálogo.
- [ ] Documentar los siete estados de orden y cuándo puede confirmarse.
- [ ] Investigar hosting, cuotas, HTTPS, CORS, persistencia y variables de entorno.
- [ ] Coordinar publicación y prueba de al menos un endpoint remoto.
- [ ] Contrastar la documentación con el código final.
- [ ] Subir los cambios a una rama propia y enlazar el PR.

## Hallazgos para coordinar con el equipo
- La rama de Comercio revisada no muestra `urls.py`, `settings.py`, `manage.py` ni migraciones.
- La vista usa `gestion_url` sin definir y busca `cliente_id` en la raíz; Gestión devuelve `usuario.id`.
- El serializador permite recibir importes desde la solicitud y no calcula precios consultando Catálogo.
- Acordar quién implementa pago sandbox, webhook, reserva/consolidación/liberación y conciliación.

Este checklist sirve para coordinar la verificación; no afirma que las tareas estén implementadas.
