
# Contrato API - Catálogo e Inventario

## Configuración

Servicio: Catálogo e Inventario
Framework: Django REST Framework
Base de datos: MongoDB
Moneda: CLP
URL local de Catálogo: configurable (ejemplo http://127.0.0.1:8000)

Los endpoints descritos son contratos propuestos para
su implementación e integración con Comercio.

## 1. Consultar producto

GET /api/productos/{id}/

Respuesta HTTP 200:

{
  "id": 1,
  "nombre": "Silla ergonomica X-fire negra",
  "precio": 150000,
  "moneda": "CLP",
  "stock_disponible": 10,
  "activo": true
}

Reglas:
- Solo se consultan productos activos.
- El precio proviene de MongoDB.
- La disponibilidad proviene de stock.disponible.
- Un producto inexistente o inactivo devuelve HTTP 404.

## 2. Reservar stock

POST /api/reservas/

Solicitud:

{
  "reserva_id": "RES-001",
  "orden_id": "ORD-001",
  "productos": [
    {
      "producto_id": 1,
      "cantidad": 2
    }
  ]
}

Respuesta HTTP 201:

{
  "reserva_id": "RES-001",
  "orden_id": "ORD-001",
  "estado": "RESERVADA",
  "fecha_expiracion": "2026-10-18T12:15:00Z"
}

Reglas:
- Cantidades enteras positivas.
- Verificar productos activos y stock disponible.
- Reservar todas las líneas o ninguna.
- Evitar reservas duplicadas.
- Una repetición idéntica devuelve HTTP 200.
- La reserva tendrá 15 minutos inicialmente.

## 3. Consolidar reserva

POST /api/reservas/{id}/consolidar/

Respuesta HTTP 200:

{
  "reserva_id": "RES-001",
  "estado": "CONSOLIDADA",
  "ya_procesada": false
}

Reglas:
- Solo para operaciones internas autorizadas.
- Comercio debe verificar previamente el pago.
- Disminuye stock.reservado.
- No modifica stock.disponible.
- No permite consolidar reservas liberadas.
- Repetir la consolidación no descuenta nuevamente.

## 4. Liberar reserva

POST /api/reservas/{id}/liberar/

Solicitud:

{
  "motivo": "PAGO_RECHAZADO"
}

Respuesta HTTP 200:

{
  "reserva_id": "RES-001",
  "estado": "LIBERADA",
  "ya_procesada": false
}

Motivos permitidos:
- PAGO_RECHAZADO
- PAGO_CANCELADO
- VENCIMIENTO_CONCILIADO

Reglas:
- Disminuye stock.reservado.
- Aumenta stock.disponible.
- No permite liberar reservas consolidadas.
- Una liberación repetida no modifica inventario.
- Los vencimientos requieren conciliación del pago.

## 5. Errores de API

HTTP 400: Datos inválidos.
HTTP 401: Autenticación requerida.
HTTP 403: Operación no autorizada.
HTTP 404: Recurso inexistente.
HTTP 409: Stock insuficiente, duplicado o conflicto de estado.
HTTP 503: Servicio temporalmente no disponible.

Formato de error:

{
  "codigo": "STOCK_INSUFICIENTE",
  "mensaje": "No existe stock suficiente"
}

## 6. Seguridad e integración

- Los precios válidos siempre provienen del backend.
- Las operaciones de reserva requieren autorización.
- Consolidar y liberar son operaciones internas protegidas.
- Los endpoints administrativos validan el token de Gestión; las reservas mantienen Bearer interno de Comercio.
- El resultado del navegador no confirma un pago.
- No se devuelve éxito cuando el resultado es incierto.
- Todas las operaciones deben respetar la idempotencia.


## 7. Contrato de inventario físico y autenticación actualizada (H2)

El documento de MongoDB almacena `stock.disponible` y `stock.reservado`.
**Stock físico = stock.disponible + stock.reservado**.

Ejemplo: disponible=15, reservado=5, físico=20.

- **Reservar**: disminuye disponible y aumenta reservado por igual; el físico no cambia.
- **Consolidar**: disminuye reservado; el físico disminuye por las unidades vendidas.
- **Liberar**: disminuye reservado y aumenta disponible; el físico no cambia.
- **RF19 (ajustar)**: fija un nuevo stock físico, conservando el reservado:
  `disponible_nuevo = stock_fisico_nuevo - stock.reservado`. Rechaza valores inferiores al reservado.

### Seguridad de las APIs

- **Administrador (persona):**
  `POST /api/productos/`, `GET /api/admin/productos/`,
  `PATCH /api/admin/productos/{id}/`,
  `PATCH /api/admin/productos/{id}/desactivar/`,
  `POST /api/admin/productos/{id}/ajustar-stock/`.
  Todas usan `Authorization: Token <token_de_Gestion>`; Catálogo consulta
  `GET /api/usuarios/verificar-token/` de Gestión, valida `ADMIN` y `ACTIVO`.
  La URL se configura mediante `GESTION_VERIFY_TOKEN_URL`.
- **Entre microservicios (Comercio):**
  `POST /api/reservas/`, `POST /api/reservas/{id}/consolidar/`
  y `POST /api/reservas/{id}/liberar/` usan
  `Authorization: Bearer <CATALOGO_INTERNAL_TOKEN>`, sin utilizar el token personal.
- Crear reserva requiere `reserva_id`, `orden_id` y `productos`
  (`producto_id`, `cantidad`); consolidar no requiere JSON obligatorio.
  Liberar requiere `motivo`: `PAGO_RECHAZADO`, `PAGO_CANCELADO`
  o `VENCIMIENTO_CONCILIADO`.
- El token de Gestión nunca debe mostrarse en el frontend ni registrarse en logs.

### Configuración al clonar

Usar `servicio_catalogo/.env.example` como referencia y configurar variables
reales en el entorno local o contenedor. **Django no carga `.env` automáticamente**.
El servidor de Gestión debe tener una URL accesible desde donde corra Catálogo.
Las reservas y RF19 requieren MongoDB compatible con transacciones (replica set).
El contrato HTTP de productos/reservas permanece compatible con Comercio.
