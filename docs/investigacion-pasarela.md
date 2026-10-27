# Investigación de Pasarelas de Pago en Ambiente Sandbox

**Asignatura:** Desarrollo de aplicaciones Web
**Entrega:** Solemne 02 – Hito 1

## 1. Introducción

El e-commerce que desarrollamos (Frontend React + Vite, Backend Django REST Framework, PostgreSQL y MongoDB) necesita un flujo de pago completo, asi que se usara una pasarela en **ambiente sandbox** que permite:

- Simular el ciclo completo de una compra (creación de transacción, pago, confirmación, rechazo) sin cobros reales ni datos sensibles de clientes.
- Validar la **arquitectura de seguridad** del sistema: el frontend nunca confirma un pago; el backend consulta a la pasarela mediante un identificador (token / id de pago) y verifica **monto** y **moneda (CLP)** antes de marcar la orden como pagada.
- Probar escenarios límite (pago aprobado, rechazado, abandonado, duplicado) de forma repetible.
- Dejar la integración lista para pasar a producción cambiando únicamente credenciales y entorno.

Este documento compara tres opciones viables que se puedan desplegar en plataformas gratuitas (Vercel, Render o Firebase), por lo que las URLs de retorno y notificación deben ser **HTTPS públicas**.

---

## 2. Opciones Evaluadas

### Opción A: Transbank Webpay Plus (ambiente Integration)

Webpay Plus es la solución de pago con tarjetas más extendida en Chile, operada por Transbank. El flujo es de **redirección**:

1. El backend crea la transacción (`create`) enviando `buy_order`, `session_id`, `amount` y `return_url`. Transbank responde con un `token` y una URL de pago.
2. El usuario es redirigido al formulario de Webpay y paga.
3. Transbank redirige al usuario a la `return_url` enviando el `token_ws`.
4. El **backend** ejecuta el `commit` (confirmación) con ese token y recibe el estado oficial (`status`, `amount`, `response_code`, `authorization_code`).
5. Opcionalmente, el backend puede consultar el estado (`status`) o reversar/anular (`refund`).

El ambiente Integration es **público y no requiere crear cuenta**: Transbank publica un código de comercio y una API Key de pruebas en su documentación oficial para Webpay Plus. Existe SDK oficial para Python (`transbank-sdk`).

### Opción B: Mercado Pago (Sandbox / Desarrollador)

Mercado Pago opera en Chile con cobros en CLP. La integración más directa para este proyecto es **Checkout Pro**, también basada en redirección:

1. El backend crea una **preferencia de pago** (`preference`) con los ítems, moneda, `back_urls` y `notification_url`.
2. El usuario es redirigido al checkout alojado por Mercado Pago (`init_point` / `sandbox_init_point`).
3. Mercado Pago notifica al backend mediante **Webhook** (`notification_url`) cuando cambia el estado del pago, enviando el id del pago.
4. El **backend** consulta `GET /v1/payments/{id}` con su Access Token y valida `status`, `transaction_amount`, `currency_id` y `external_reference`.

Requiere cuenta de desarrollador, una aplicación creada en el panel y **usuarios de prueba** (vendedor y comprador) para operar en sandbox. Existe SDK oficial para Python (`mercadopago`) y la API REST es sencilla de consumir con `requests`.

### Opción C: Flow (ambiente Sandbox)

Flow es una pasarela chilena que agrupa varios medios de pago (tarjetas, transferencia, Webpay, entre otros) detrás de una única API REST, con un ambiente sandbox propio (`sandbox.flow.cl`). El flujo es de **redirección con confirmación server-to-server**:

1. El backend llama a `payment/create` con `commerceOrder`, `subject`, `amount`, `email`, `currency` (CLP), `urlConfirmation` y `urlReturn`. Flow responde con un `token` y una URL de pago.
2. El usuario es redirigido a Flow y completa el pago.
3. Flow hace una petición **POST a `urlConfirmation`** (webhook) con el `token` del pago, de forma independiente al navegador del usuario.
4. El **backend** consulta `payment/getStatus` con ese token y valida `status` (2 = pagada), `amount`, `currency` y `commerceOrder`.
5. Flow también redirige al usuario a `urlReturn`, que solo debe usarse para mostrar el resultado, nunca para confirmar.

Cada petición se firma con **HMAC-SHA256** usando la `secretKey` de la cuenta (parámetros ordenados alfabéticamente). Requiere crear una cuenta en el sandbox para obtener `apiKey` y `secretKey`. No depende de un SDK oficial de Python: se integra con `requests`.

---

## 3. Comparativa Técnica

| Criterio | Transbank Webpay Plus (Integration) | Mercado Pago (Sandbox) | Flow (Sandbox) |
|---|---|---|---|
| **Soporte CLP** | Nativo. CLP por defecto; montos enteros sin decimales. | Sí, con cuenta/sitio de Chile (`currency_id: "CLP"`). Los usuarios de prueba deben ser de Chile. | Nativo. CLP es la moneda principal (`currency: "CLP"`). |
| **Webhooks** | **No ofrece webhooks.** Confirmación por redirección a `return_url` con `token_ws` y `commit` desde el backend; se complementa con consulta de estado (`status`) y reconciliación. | **Sí.** Webhooks (e IPN) hacia `notification_url`, con firma verificable (`x-signature`). El backend igualmente consulta la API. | **Sí.** POST server-to-server a `urlConfirmation` con el `token`; el backend consulta `getStatus` para validar. |
| **Facilidad de integración en Django** | 3 operaciones (`create`, `commit`, `status`) y SDK oficial. | Requiere endpoint de webhook, validación de firma, estados intermedios e idempotencia. | API REST pequeña (`create`, `getStatus`), pero hay que implementar la firma HMAC y el cliente HTTP a mano (sin SDK oficial en Python). |
| **Registro y uso** | Credenciales públicas, sin registro, un único flujo documentado. |  Cuenta, aplicación, usuarios de prueba, estados de pago y notificaciones. | Registro en sandbox y firma de parámetros, flujo  claro (token, webhook, consulta). |
| **HTTPS / Despliegue** | `return_url` accesible desde el navegador; en Integration funciona incluso con `localhost`. En producción conviene HTTPS público. No requiere que Transbank llegue a nuestro servidor. | `notification_url` **debe ser HTTPS pública**; en local requiere túnel (ngrok). En Render gratuito el servicio "duerme" y puede retrasar el webhook. | `urlConfirmation` **debe ser HTTPS pública**; en local requiere túnel. Mismo riesgo de "dormido" en Render gratuito, atenuado porque Flow reintenta la confirmación. |
| **Seguridad (verificación backend)** | Valida `amount`, `buy_order` y `status = AUTHORIZED` en el `commit`. | Valida `status = approved`, `transaction_amount`, `currency_id` y `external_reference`, además de la firma del webhook. | Valida `status = 2`, `amount`, `currency` y `commerceOrder` en `getStatus`; el token del webhook por sí solo no confirma nada. |
| **Uso en producción Chile** | Muy alta: estándar del comercio chileno. | Alta, con otro modelo de cuentas y comisiones. | Alta: muy usada por pymes chilenas; ofrece múltiples medios de pago en una sola integración. |


---

## 4. Opciones de uso para el Equipo

**Opción 1: Transbank Webpay Plus (ambiente Integration).**

**Opcion 2: Flow.** 

**Justificación de la opción principal:**

1. No requiere registro ni usuarios de prueba: las credenciales de Integration son públicas. 
2. **Flujo simple** El diseño (`create` → redirección → `commit` desde el backend) 
3. No depende de un webwook entrante, evita perdida de notificaciones.

**Flow la segunda opcion:** elegir si se requiere **webhooks reales**, la API es más pequeña (flujo token → webhook → consulta, pasarela chilena con CLP nativo). Su costo es el registro en sandbox, la firma HMAC manual y la necesidad de una URL pública para `urlConfirmation`.

---

## 5. Backend - Webpay Plus

1. **Dependencias y configuración**
   - Instalar `transbank-sdk` y agregarlo a `requirements.txt`.
   - Definir en variables de entorno (no en el repositorio): `TBK_COMMERCE_CODE`, `TBK_API_KEY`, `TBK_ENVIRONMENT=integration` y `TBK_RETURN_URL` (HTTPS pública del backend o frontend).
   - Cargar estas variables en `settings.py` y configurar CORS para el dominio del frontend (Vercel).



## 6. Bibliografía

**Transbank Webpay Plus**
- Cómo empezar (ambientes y códigos de comercio): https://transbankdevelopers.cl/documentacion
- Documentación Webpay Plus: https://transbankdevelopers.cl/documentacion/webpay-plus
- Referencia de API: https://transbankdevelopers.cl/referencia

**Mercado Pago**
- Compras de prueba con Checkout Pro (Chile): https://www.mercadopago.cl/developers/es/docs/checkout-pro/integration-test/test-purchases
- SDKs oficiales (lado servidor): https://www.mercadopago.com/developers/en/docs/sdks-library/server-side
- SDK oficial de Python (GitHub): https://github.com/mercadopago/sdk-python

**Flow**
- Referencia API REST: https://developers.flow.cl/api
- Quick Start (incluye ejemplo en Python): https://developers.flow.cl/docs/quick-start
- Ambiente Sandbox: https://sandbox.flow.cl