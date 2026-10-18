# Checklist de entrega — Matías (Escuadrón 3)

Usa esta lista para distinguir documentación de funcionalidad implementada. No marques como terminado un despliegue o endpoint hasta probarlo realmente.

## Documentación
- [ ] Revisar `docs/estados-orden.md` existente y alinearlo con el contrato.
- [ ] Revisar `docs/investigacion-despliegue.md` existente y contrastar límites con documentación oficial vigente.
- [ ] Añadir `docs/arquitectura-general.md`.
- [ ] Añadir `docs/contrato-api-servicios.md`.
- [ ] Validar diagramas, propiedad de datos y rutas con el equipo.
- [ ] Quitar la etiqueta de borrador solo después de acordar las decisiones.

## Validaciones técnicas
- [ ] Comercio calcula los importes en backend.
- [ ] Inventario valida stock al reservar.
- [ ] Reservar, liberar y consolidar toleran reintentos.
- [ ] Webhook verificado e idempotente según la pasarela.
- [ ] La orden no pasa a `CONFIRMADA` sin pago verificado y stock consolidado.
- [ ] Los fallos parciales se pueden recuperar y conciliar.

## Despliegue
- [ ] Elegir plataforma con el equipo y revisar límites vigentes.
- [ ] `DEBUG=False`, `ALLOWED_HOSTS` correcto y secretos en variables de entorno.
- [ ] CORS limitado al origen real del frontend.
- [ ] Base de datos persistente configurada.
- [ ] HTTPS y URL HTTPS de webhook si corresponde.
- [ ] Ejecutar `python manage.py check --deploy`.
- [ ] Publicar un endpoint no sensible de salud/documentación.
- [ ] Probarlo desde internet y guardar URL y evidencia.
- [ ] Documentar cuotas y restricciones.

## Git
- [ ] Usar la rama personal solicitada por el equipo.
- [ ] Hacer commits pequeños y descriptivos de cambios reales.
- [ ] No subir `.env`, secretos ni datos sensibles.
- [ ] Confirmar que los cambios están en la rama correcta.
- [ ] Cumplir el mínimo de 7 contribuciones significativas por integrante con cambios reales, no commits artificiales.

## Nota sobre Render gratuito
La documentación oficial indica que los servicios web gratuitos se suspenden tras 15 minutos sin tráfico y pueden tardar cerca de un minuto en volver. El sistema de archivos gratuito es efímero. El PostgreSQL gratuito tiene límite de 1 GB y caduca a los 30 días, por lo que no debe asumirse como base persistente para todo el semestre. Verificar la información vigente antes de desplegar: https://render.com/docs/free

Render es una opción investigada, no una plataforma definitiva ya acordada.
