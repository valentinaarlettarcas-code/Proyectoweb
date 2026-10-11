# Estados de orden — Servicio Comercio

**Proyecto:** Solemne 02 — Desarrollo de Aplicaciones Web  
**Responsabilidad:** Escuadrón 3 — Comercio (carrito, órdenes, pagos y conciliación)  
**Estado del documento:** propuesta funcional para revisión y aprobación del equipo.

## 1. Objetivo

Definir los estados de una orden y las reglas que permiten coordinar el pago con la reserva y consolidación del inventario. La orden debe reflejar el resultado real del proceso y no solamente la respuesta que ve el cliente en el navegador.

## 2. Estados requeridos

| Estado | Definición funcional |
|---|---|
| `PENDIENTE_PAGO` | La orden fue creada y espera el resultado del proceso de pago. |
| `CONFIRMACION_PENDIENTE` | El pago fue aprobado/verificado, pero todavía falta completar la confirmación o consolidación del inventario. |
| `CONFIRMADA` | El pago está verificado y el inventario quedó consolidado correctamente. |
| `RECHAZADA` | El pago fue rechazado y la orden no se debe confirmar. |
| `CANCELADA` | La orden fue cancelada conforme a las reglas del negocio. Si existía una reserva, debe liberarse cuando corresponda. |
| `VENCIDA` | Se agotó el plazo permitido para completar el proceso de compra. Se deben ejecutar las acciones de liberación que correspondan. |
| `REVISION_REQUERIDA` | Existe una inconsistencia o resultado no concluyente que requiere conciliación antes de determinar el resultado final. |

## 3. Invariantes y reglas de negocio

1. **Condición de confirmación:** una orden solo puede pasar a `CONFIRMADA` cuando el servidor ha verificado el pago y el inventario se ha consolidado correctamente.
2. **Verificación del lado servidor:** no confiar únicamente en una pantalla de éxito o en datos enviados por el navegador.
3. **Idempotencia:** una notificación repetida del proveedor de pago no debe duplicar cambios de estado ni operaciones de inventario. Registrar y reconocer los identificadores de eventos procesados.
4. **Reserva de inventario:** reservar unidades durante el flujo de compra y consolidarlas o liberarlas según el resultado final, evitando vender más unidades de las disponibles.
5. **Fallos entre servicios:** si el pago se aprueba pero inventario no responde o no puede consolidarse, no confirmar la orden. Mantenerla pendiente o enviarla a `REVISION_REQUERIDA` según el resultado de los reintentos y la conciliación.
6. **Trazabilidad:** registrar fechas, identificadores de orden y de evento de pago, cambios de estado y errores relevantes, sin guardar secretos ni datos de pago sensibles innecesarios.
7. **Snapshot histórico:** guardar en la orden los datos relevantes del producto, precio, cantidad y descripción al momento de comprar, aunque el catálogo cambie después.
8. **Sandbox:** todas las pruebas de pago deben usar el entorno sandbox; no realizar cobros reales.

## 4. Flujo funcional de referencia

1. Crear la orden en `PENDIENTE_PAGO`.
2. Iniciar el proceso de pago con el proveedor sandbox.
3. Si el pago se rechaza, cambiar a `RECHAZADA` y liberar la reserva si corresponde.
4. Si el pago se aprueba, comprobar el resultado en el servidor. Mientras falte consolidar inventario, utilizar `CONFIRMACION_PENDIENTE`.
5. Cuando el pago está verificado y la consolidación de inventario termina correctamente, cambiar a `CONFIRMADA`.
6. Si se agota el plazo, aplicar `VENCIDA` y liberar la reserva cuando corresponda.
7. Si el usuario o una regla del sistema cancela la compra, aplicar `CANCELADA` y gestionar la reserva.
8. Si el resultado del pago o del inventario no se puede determinar con seguridad, usar `REVISION_REQUERIDA` y ejecutar conciliación; no asumir que la compra está confirmada.

## 5. Tabla de decisión mínima

| Situación | Resultado esperado |
|---|---|
| Orden creada, esperando pago | `PENDIENTE_PAGO` |
| Pago rechazado | `RECHAZADA` |
| Pago aprobado, consolidación pendiente | `CONFIRMACION_PENDIENTE` |
| Pago verificado e inventario consolidado | `CONFIRMADA` |
| Se agotó el plazo sin completar la compra | `VENCIDA` |
| Cancelación válida | `CANCELADA` |
| Evento contradictorio o resultado incierto | `REVISION_REQUERIDA` |

## 6. Pruebas de aceptación

- Un pago rechazado nunca confirma la orden.
- Un pago aprobado no confirma la orden mientras falte consolidar inventario.
- Si el pago está verificado y el inventario se consolida, la orden queda confirmada.
- Procesar dos veces el mismo webhook no duplica efectos.
- Una orden vencida o cancelada libera su reserva conforme a las reglas acordadas.
- Si un servicio no responde, el sistema no inventa un resultado exitoso y permite reintentar o conciliar.
- El precio y la información histórica de la compra se mantienen aunque el producto cambie posteriormente.

## 7. Acuerdos que debe validar el equipo

- Tiempo límite de una orden pendiente.
- Cuándo corresponde `CANCELADA` y cuándo `VENCIDA`.
- Política de reintentos y plazo antes de escalar a `REVISION_REQUERIDA`.
- Identificador usado para detectar webhooks duplicados.
- Mecanismo para reconciliar un pago aprobado con una reserva de inventario fallida.
- Transiciones permitidas y prohibidas para evitar cambios de estado contradictorios.

**Nota:** las definiciones son una propuesta funcional basada en los estados requeridos por la evaluación. Los plazos y algunos detalles de transición son decisiones de implementación que deben acordarse con el equipo.
