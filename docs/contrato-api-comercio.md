# Contrato de API del servicio Comercio

Servicio de órdenes y pagos de SetupVerse. La moneda es el peso chileno (CLP), sin decimales.

## Autenticación

Todos los endpoints exigen el encabezado `Authorization: Token <token>`. El token se obtiene al iniciar sesión en el servicio de Gestión (`POST /api/usuarios/login/`).

Comercio no guarda usuarios. En cada petición consulta `GET /api/usuarios/verificar-token/` en Gestión, que responde con los datos del usuario dentro de la clave `usuario` (`id`, `email`, `rol` y `estado`). Solo puede operar un usuario con rol `CLIENTE` y estado `ACTIVO`, así que un administrador no puede comprar. La dirección de Gestión se configura con la variable de entorno `GESTION_VERIFY_TOKEN_URL`.

## Formato de los datos

- Los importes (`total_amount`, `historical_price`, `subtotal`) se envían como texto sin decimales, por ejemplo `"29990"`.
- El importe del intento de pago se envía como texto con dos decimales, por ejemplo `"29990.00"`.
- Los identificadores y las cantidades se envían como número, salvo `producto_id` dentro de las líneas de la orden, que se devuelve como texto.

## Crear orden

`POST /api/ordenes/`

Cuerpo de la petición:

    {
      "checkout_id": "checkout-2026-0001",
      "items": [
        { "producto_id": 12, "quantity": 2 }
      ]
    }

Reglas:

- `checkout_id`: texto obligatorio, de hasta 255 caracteres. Identifica la operación de compra.
- `items`: al menos una línea. No se puede repetir un producto: se combinan las cantidades en una sola línea.
- `producto_id`: número entero mayor o igual a 1.
- `quantity`: número entero entre 1 y 100.

El cliente nunca envía precios, nombres, moneda ni totales. Comercio consulta cada producto en Catálogo (`GET /api/productos/<id>/`) y calcula todo. Si un producto no existe, está inactivo, no tiene stock suficiente o no está en CLP, se rechaza la orden completa.

Repetición segura: si el mismo cliente envía otra vez el mismo `checkout_id`, se devuelve la orden ya creada con código 200, sin crear otra. Dos clientes distintos pueden usar el mismo `checkout_id`.

Respuesta exitosa (201 al crear, 200 al repetir):

    {
      "id": 7,
      "cliente_id": 45,
      "checkout_id": "checkout-2026-0001",
      "status": "PENDIENTE_PAGO",
      "total_amount": "29990",
      "moneda": "CLP",
      "created_at": "2026-10-27T11:30:00Z",
      "items": [
        {
          "producto_id": "12",
          "historical_product_name": "Teclado mecánico",
          "historical_price": "14995",
          "moneda": "CLP",
          "quantity": 2,
          "subtotal": "29990"
        }
      ]
    }

Los datos históricos de cada línea (nombre, precio y moneda) quedan guardados en la orden y no cambian aunque el producto se modifique después. El estado inicial es siempre `PENDIENTE_PAGO`; los demás estados están en `docs/estados-orden.md`.

Errores:

| Código | Cuándo |
|---|---|
| 400 | Datos inválidos. El cuerpo indica el campo afectado (`checkout_id` o `items`) |
| 403 | Token ausente o inválido, usuario que no es `CLIENTE` o cuenta que no está `ACTIVO` |
| 503 | El servicio de Gestión no está disponible |

## Consultar una orden

`GET /api/ordenes/<id>/`

Devuelve la orden con el mismo formato de arriba. Un cliente solo puede ver sus propias órdenes: si la orden no existe o pertenece a otro cliente, la respuesta es 404, sin revelar cuál de los dos casos es. Los errores de autenticación son los mismos de la creación.

## Crear intento de pago

`POST /api/ordenes/<id>/payment-attempts/`

Cuerpo de la petición:

    { "return_url": "http://localhost:5173/pago/retorno" }

El importe y la moneda se toman de la orden, nunca de la petición. La pasarela es Transbank Webpay Plus (ambiente de pruebas).

Reglas y respuestas:

- La orden debe ser del cliente autenticado (si no, 404) y estar en estado `PENDIENTE_PAGO` (si no, 409 con el código `INVALID_STATE_TRANSITION`).
- Si la orden ya tiene un intento pendiente, se devuelve ese mismo intento con código 200, para evitar intentos duplicados.
- Si no, se crea el intento en Transbank y se responde 201. La respuesta incluye el intento con su estado y los datos para redirigir al cliente a la página de pago de Webpay Plus.
- Si Transbank falla, se responde 502 y el intento queda marcado para revisión. Nunca se informa éxito cuando no se conoce el resultado.

Errores de autenticación en este endpoint:

| Código | Cuándo |
|---|---|
| 401 | Token ausente, inválido o no confirmado por Gestión |
| 503 | El servicio de Gestión no está disponible |

Webpay Plus no usa webhook: el cliente vuelve a `return_url` con un `token_ws` y es el servidor quien confirma la transacción con Transbank.

## Estado de implementación

Pendiente (Sprint 6, HU-12 a HU-14):

- Reservar stock en Catálogo al crear la orden (`POST /api/reservas/`, autenticado con `CATALOGO_INTERNAL_TOKEN`).
- Confirmar la transacción al volver de Webpay, verificando autorización, importe y moneda, sin procesar dos veces el mismo resultado.
- Consolidar el stock, confirmar la orden y liberar la reserva si el pago falla.
- Hoy, si Catálogo no está disponible, la creación de la orden responde 400; debe responder 503.
- Unificar los códigos de autenticación de los dos endpoints (comprobado con el servicio en ejecución: hoy 403 en órdenes y 401 en pagos).

## Configuración

Variables de entorno de Comercio: `GESTION_VERIFY_TOKEN_URL`, `CATALOGO_API_BASE_URL` (sin `/api` al final), `CATALOGO_INTERNAL_TOKEN`, `TBK_COMMERCE_CODE`, `TBK_API_KEY`, `TBK_ENVIRONMENT`, `TBK_RETURN_URL` y las de la base de datos (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` y `DB_PORT`). Los valores de ejemplo, sin datos reales, están en `.env.example`.