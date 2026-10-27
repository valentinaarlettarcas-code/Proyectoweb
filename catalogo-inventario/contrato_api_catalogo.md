
# Contrato API - Catálogo e Inventario

## Configuración

Servicio: Catálogo e Inventario
Framework: Django REST Framework
Base de datos: MongoDB
Moneda: CLP
URL local: http://127.0.0.1:8001

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
- La autenticación se integrará con el servicio de Gestión.
- El resultado del navegador no confirma un pago.
- No se devuelve éxito cuando el resultado es incierto.
- Todas las operaciones deben respetar la idempotencia.
