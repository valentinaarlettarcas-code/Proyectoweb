# Contrato API entre servicios — Solemne 02

**Estado:** borrador. Confirmar prefijos raíz y endpoints de Comercio con el código final.

## Gestión — verificar token
- **Método/ruta:** `GET /api/usuarios/verificar-token/`
- La implementación actual usa autenticación por token de DRF.
- Respuesta válida esperada: `{"valido":true,"usuario":{"id":123,"email":"cliente@example.com","rol":"cliente","estado":"activo"}}`
- Comercio debe leer `usuario.id`, no `cliente_id` en la raíz.
- Si el token es inválido o Gestión no responde, no crear la orden.

## Catálogo/Inventario — consultar producto
- **Método/ruta:** `GET /api/productos/{id}/` (confirmar prefijo raíz).
- La vista actual es pública.
- Respuesta esperada: `{"id":1,"nombre":"Producto","precio":10000,"moneda":"CLP","stock_disponible":5,"activo":true}`
- El backend de Comercio debe usar el precio devuelto por Catálogo.

## Catálogo/Inventario — crear reserva
- **Método/ruta:** `POST /api/reservas/`
- **Autenticación interna actual:** `Authorization: Bearer <CATALOGO_INTERNAL_TOKEN>`
- Solicitud: `{"reserva_id":"res-123","orden_id":"ord-123","productos":[{"producto_id":1,"cantidad":2}]}`
- Respuesta: `201 Created` para una reserva nueva; `200 OK` para una repetición idéntica.

## Catálogo/Inventario — consolidar y liberar
- **Consolidar:** `POST /api/reservas/{id}/consolidar/`; solo tras verificar el pago.
- **Liberar:** `POST /api/reservas/{id}/liberar/` con `{"motivo":"PAGO_RECHAZADO"}`.
- Motivos admitidos: `PAGO_RECHAZADO`, `PAGO_CANCELADO`, `VENCIMIENTO_CONCILIADO`.
- Ambas operaciones usan la autenticación interna actual y deben ser idempotentes.

## Comercio — contrato objetivo pendiente de verificar
La rama revisada no contiene configuración de rutas de Comercio. Estas rutas son propuestas, no endpoints confirmados:
- `POST /api/ordenes/`: validar token, precios, productos y crear orden.
- `GET /api/ordenes/{id}/`: consultar una orden propia.
- Webhook de pago sandbox: ruta por definir según el proveedor.
- Proceso de conciliación: por definir.

## Estados de orden
- `PENDIENTE_PAGO`: esperando resultado del pago.
- `CONFIRMACION_PENDIENTE`: pago verificado, falta consolidar inventario.
- `CONFIRMADA`: pago verificado e inventario consolidado.
- `RECHAZADA`: pago rechazado.
- `CANCELADA`: compra cancelada.
- `VENCIDA`: venció el plazo.
- `REVISION_REQUERIDA`: resultado incierto que requiere conciliación.

## Reglas comunes
- Usar HTTPS y variables de entorno para secretos.
- Configurar timeout y errores controlados en llamadas entre servicios.
- No confiar en precios enviados por el frontend.
- No duplicar efectos al recibir solicitudes o webhooks repetidos.
- No confirmar una orden ante resultados inciertos.
