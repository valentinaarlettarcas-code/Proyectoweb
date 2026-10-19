# Integración Transbank Webpay Plus — HU-13

**Responsable:** Charlotte (Escuadrón 3)
**RF cubiertos:** RF-31 (Iniciar pago en sandbox)
**Estado:** implementación inicial para H1/H2.

## 1. Pasarela elegida

**Transbank Webpay Plus**, ambiente Integration (sandbox).

Justificación (basada en `docs/investigacion-pasarela.md`):
- Credenciales de Integration públicas, sin registro ni usuarios de prueba.
- Flujo simple: `create` → redirección → `commit` (H3).
- CLP nativo (sin conversiones).
- No depende de webhooks entrantes (importante para plataformas gratuitas
  con sleep como Render).

## 2. Credenciales de sandbox

| Variable | Valor (público, sandbox) |
|---|---|
| `TBK_COMMERCE_CODE` | `597055555532` |
| `TBK_API_KEY` | `579B532A7440BB0C9079DED94D31EA9F33E66819` |
| `TBK_ENVIRONMENT` | `TEST` |

Fuente: <https://transbankdevelopers.cl/documentacion>

Estas credenciales están en el `.env.example` y no son secretas. En producción
se reemplazan por las del comercio real **sin subirlas al repo**.

## 3. Tarjetas de prueba

| Escenario | Tarjeta | CVV | Expiración |
|---|---|---|---|
| Pago aprobado | `4051 8856 0044 6623` | `123` | cualquier fecha futura |
| Pago rechazado | `5186 0000 0000 0000` | `123` | cualquier fecha futura |

RUT del comprador: `11.111.111-1`.

## 4. Flujo implementado (HU-13)

```
Frontend (Checkout.jsx)
   |
   | 1. POST /api/v1/orders/   { items: [...] }
   v
Comercio (Django)
   |-- Lee precios a Catalogo/Inventario (TODO)
   |-- Crea Orden PENDIENTE_PAGO con snapshot de lineas (RF-08, RF-28)
   |-- Calcula total y moneda en backend (CC-06)
   |
   | 2. POST /api/v1/orders/{id}/payment-attempts/   { return_url }
   v
Comercio -> Transbank (SDK: Transaction.create)
   |-- buy_order  (unico por intento)
   |-- session_id
   |-- amount     (entero en CLP)
   |-- return_url
   |
   v
Transbank responde: { token, url }
   |
   | Comercio guarda token_ws y checkout_url en IntentoPago
   | Responde al frontend con checkout_url
   v
Frontend: window.location.href = checkout_url
   |
   | (Usuario paga en formulario hosted de Transbank)
   v
Transbank redirige a /pago/retorno?token_ws=...
   |
   v
Frontend (RetornoPago.jsx): muestra token_ws
```

## 5. Lo que NO está en HU-13 (va en H3)

- RF-32: `Transaction.commit(token_ws)` para verificar el resultado.
- RF-33: consolidar inventario tras pago aprobado.
- RF-34: marcar orden CONFIRMADA.
- RF-30: liberar reserva ante rechazo o vencimiento.
- Webhook declarativo ya existe en `/api/v1/payments/webhook/` pero solo
  retorna 200 OK. Transbank Webpay Plus no lo usa para Webpay Plus normal,
  pero queda declarado para migrar a MercadoPago/Flow si fuera necesario.

## 6. Idempotencia

Implementada a nivel de endpoint:

- Si la orden ya tiene un `IntentoPago` con `estado=PENDIENTE`, el endpoint
  devuelve ese intento (status 200) en lugar de crear uno nuevo.
- Esto cubre el caso de doble clic en el botón "Pagar".
- El frontend además bloquea el botón mientras está cargando (doble protección).

## 7. Validaciones implementadas

| Regla | Dónde | Cómo |
|---|---|---|
| CC-06: monto y moneda del backend | `views.py` | Lee `orden.total` y `orden.moneda` |
| RF-27: orden en PENDIENTE_PAGO | `views.py` | Rechaza 409 si la orden está en otro estado |
| CC-03: error identificable | `serializers.py` | `return_url` validada contra lista blanca |
| RF-31: sin duplicados | `views.py` | `get_or_create` implícito sobre intentos PENDIENTE |

## 8. Pendientes de coordinación con el equipo

- [ ] Acordar con Jani si `Orden` vive en `pagos/models.py` (como está ahora)
      o se mueve a `comercio/ordenes/models.py`.
- [ ] Acordar con Matías el campo `cliente_id` (¿UUID de Gestión? ¿email?).
- [ ] Integrar auth con Gestión (Bearer token / sesión Django) para validar
      que el cliente es dueño de la orden (RF-10, CC-02).
- [ ] Llamar a Catalogo/Inventario para reservar stock antes de crear el
      intento (RF-29). Hoy se asume que la orden ya tiene `reserva_id`.

## 9. Referencias

- Transbank Webpay Plus: <https://transbankdevelopers.cl/documentacion/webpay-plus>
- SDK Python: <https://github.com/TransbankDevelopers/transbank-sdk-python>
- Tarjetas de prueba: <https://transbankdevelopers.cl/documentacion/como_empezar#ambiente-de-pruebas>
