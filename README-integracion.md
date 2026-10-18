# Servicio Comercio: parche inicial de integración

## Qué corrige
- Define un proyecto Django ejecutable para Comercio (`manage.py`, `config/`, rutas y WSGI/ASGI).
- Corrige la lectura del ID de usuario desde `usuario.id` en la respuesta de Gestión.
- Añade timeout a llamadas remotas.
- No acepta precios, subtotales ni total desde el frontend; consulta precios actuales a Catálogo y calcula importes en el servidor.
- Guarda orden e ítems en una transacción de base de datos.

## Variables de entorno
- `DJANGO_SECRET_KEY`: obligatoria para despliegue.
- `DJANGO_DEBUG`: `false` por defecto.
- `DJANGO_ALLOWED_HOSTS`: dominios separados por coma.
- `GESTION_VERIFY_TOKEN_URL`: URL completa del endpoint de verificación, por ejemplo `https://gestion.example.com/api/usuarios/verificar-token/`.
- `CATALOGO_API_BASE_URL`: URL base del servicio Catálogo, sin `/api` al final.
- `DATABASE_URL`: opcional; si no existe se usa SQLite solo para desarrollo local.

El token de Gestión debe enviarse como `Authorization: Token <token>`, que es el formato usado por DRF TokenAuthentication.

## API expuesta
- `POST /api/ordenes/`
  ```json
  {
    "checkout_id": "checkout-unico-123",
    "items": [
      {"producto_id": 1, "quantity": 2}
    ]
  }
  ```
- `GET /api/ordenes/<id>/`: solo devuelve una orden cuyo `cliente_id` coincida con el usuario autenticado.

## Limitaciones pendientes (no afirmar que el proyecto ya está completo)
Este parche es una base de integración, no un checkout terminado. Todavía se debe implementar y probar:
1. Reserva de inventario usando `POST /api/reservas/` y compensación/liberación si falla un paso.
2. Proveedor de pagos sandbox, verificación del pago y webhook autenticado.
3. Consolidación de stock solo después de confirmar el pago; liberación en rechazo/cancelación/vencimiento.
4. Idempotencia de checkout y webhooks, conciliación de resultados inciertos.
5. Migraciones, pruebas automatizadas y despliegue real.
6. Ajustar `estado` de Gestión según los valores exactos del enum del modelo; validar contrato con respuestas reales.
7. Añadir una prueba de extremo a extremo entre los tres servicios antes de integrar a `main`.

## Aplicación
Integra estos archivos en una rama de trabajo de Comercio. Ejecuta:
`python -m pip install -r requirements.txt`
`python manage.py check`
`python manage.py makemigrations comercio`
`python manage.py migrate`
`python manage.py runserver`

No subas secretos al repositorio. No despliegues con `DEBUG=true`.
