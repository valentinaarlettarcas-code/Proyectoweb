# Integración Transbank Webpay Plus — HU-13

**Responsable:** Charloth (Escuadrón 3)
**RF cubiertos:** RF-31 (Iniciar pago en sandbox)
**Estado:** implementación inicial para H1.

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
| `TBK_API_KEY` | `579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C` |
| `TBK_ENVIRONMENT` | `TEST` |

Fuente: SDK Python `transbank-sdk==6.1.0`, constantes en
`transbank.common.integration_api_keys` y `transbank.common.integration_commerce_codes`.

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
   | 1. POST /api/dev/crear-orden-prueba/   { checkout_id }
   |    (modo dev: omite Gestion y Catalogo)
   v
Comercio (Django) — app pagos
   |-- Crea Order PENDIENTE_PAGO (modelo de Matias en comercio/)
   |-- Snapshot de lineas (RF-08, RF-28)
   |
   | 2. POST /api/ordenes/<id>/payment-attempts/   { return_url }
   v
Comercio -> Transbank (SDK: Transaction.create)
   |-- buy_order  (unico por intento)
   |-- session_id
   |-- amount     (entero en CLP, leido de Order.total_amount)
   |-- return_url (validada contra lista blanca)
   |
   v
Transbank responde: { token, url } (dict en SDK 6.x)
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

## 5. Endpoints

| Método | Ruta | App | Descripción |
|---|---|---|---|
| `POST` | `/api/ordenes/` | comercio (Matias) | Crear orden real |
| `GET` | `/api/ordenes/<id>/` | comercio (Matias) | Consultar orden |
| `POST` | `/api/ordenes/<id>/payment-attempts/` | pagos (Charloth) | Crear intento de pago |
| `POST` | `/api/payments/webhook/` | pagos (Charloth) | Webhook declarativo |
| `POST` | `/api/dev/crear-orden-prueba/` | pagos (Charloth) | **Solo dev**: crea orden sin Gestion ni Catalogo |

## 6. Modo desarrollo

Para probar el flujo completo sin Gestion ni Catalogo corriendo:

- **Bypass de auth**: si `DJANGO_DEBUG=True` y `Authorization: Token dev-test`,
  el endpoint acepta la petición sin consultar a Gestion.
- **Endpoint dev**: `/api/dev/crear-orden-prueba/` crea una Order ficticia
  con productos de prueba (Teclado Mecanico Dev, $30.000 CLP).
- **Frontend dev**: `/dev/checkout` usa estos endpoints para demostrar
  el flujo de pago completo.

En producción (`DEBUG=False`), el bypass y el endpoint dev quedan
automáticamente desactivados.

## 7. Lo que NO está en HU-13 (va en H3)

- RF-32: `Transaction.commit(token_ws)` para verificar el resultado.
- RF-33: consolidar inventario tras pago aprobado.
- RF-34: marcar orden CONFIRMADA.
- RF-30: liberar reserva ante rechazo o vencimiento.
- Webhook declarativo ya existe en `/api/payments/webhook/` pero solo
  retorna 200 OK. Webpay Plus no lo usa, queda declarado para H3.

## 8. Idempotencia

Implementada a nivel de endpoint:

- Si la orden ya tiene un `IntentoPago` con `status=PENDIENTE`, el endpoint
  devuelve ese intento (status 200) en lugar de crear uno nuevo.
- Esto cubre el caso de doble clic en el botón "Pagar".
- El frontend además bloquea el botón mientras está cargando (doble protección).

## 9. Validaciones implementadas

| Regla | Dónde | Cómo |
|---|---|---|
| CC-02: cliente activo | `views.py` `_verificar_token` | Consulta Gestion (o bypass en dev) |
| CC-04: propiedad de la orden | `views.py` `CrearIntentoPagoView` | `order.cliente_id == cliente_id` |
| CC-06: monto y moneda del backend | `views.py` | Lee `order.total_amount` y `order.moneda` |
| RF-10: cliente solo paga sus ordenes | `views.py` | Valida propiedad antes de crear intento |
| RF-27: orden en PENDIENTE_PAGO | `views.py` | Rechaza 409 si la orden está en otro estado |
| RF-31: sin duplicados | `views.py` | Devuelve intento existente si hay PENDIENTE |

## 10. Estructura de archivos

```
comercio/
├── manage.py                         
├── requirements.txt                 
├── .env.example                      
├── config/                           
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── comercio/                         
│   ├── models.py                     (Order, OrderItem)
│   ├── serializers.py
│   ├── views.py                      (CrearOrdenView, DetalleOrdenView)
│   └── urls.py
└── pagos/                            
    ├── models.py                     (IntentoPago con FK a Order)
    ├── serializers.py
    ├── views.py                      (CrearIntentoPagoView, webhook, dev)
    ├── urls.py
    └── admin.py
```

## 11. Pendientes de coordinación con el equipo

- [ ] Integrar con Gestion real cuando este disponible (RF-10).
- [ ] Integrar con Catalogo/Inventario real para reservar stock (RF-29).
- [ ] Resolver el endpoint `/api/ordenes/` real con auth de Gestion.
- [ ] En H3: implementar `Transaction.commit` en el retorno.

## 12. Referencias

- Transbank Webpay Plus: <https://transbankdevelopers.cl/documentacion/webpay-plus>
- SDK Python: <https://github.com/TransbankDevelopers/transbank-sdk-python>
- Tarjetas de prueba: <https://transbankdevelopers.cl/documentacion/como_empezar#ambiente-de-pruebas>
