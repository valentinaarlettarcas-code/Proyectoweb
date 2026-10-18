# Catálogo e Inventario — evidencia Carlos, Sprint 2

## Entregas propias
- Microservicio Django REST Framework separado de los demás escuadrones.
- Contrato API: GET `/api/productos/{id}/`, POST `/api/reservas/`, POST `/api/reservas/{id}/consolidar/` y POST `/api/reservas/{id}/liberar/`.
- HU-08 iniciada: POST `/api/productos/` con validación de precio positivo, stock entero no negativo, 4–6 imágenes; conservación de `stock.reservado` y `stock.disponible`.
- Pruebas aisladas con `unittest` y Django `SimpleTestCase`; las simulaciones NO prueban MongoDB real.

## Puesta en marcha desde copia limpia (solo microservicio)
1. Crear y activar un entorno virtual Python compatible.
2. Instalar dependencias: `python -m pip install -r requirements-catalogo.txt`.
3. Configurar variables de entorno sin guardarlas en Git:
   - `DJANGO_SECRET_KEY`: clave secreta aleatoria (obligatoria).
   - `CATALOGO_MONGO_URI`: URI del MongoDB `catalogo_db` (necesaria para consultas/escrituras reales).
   - `CATALOGO_INTERNAL_TOKEN`: token interno provisional para reservas (desarrollo).
   - `CATALOGO_ADMIN_TOKEN`: token administrativo provisional independiente (desarrollo).
4. `python manage.py check`
5. `python manage.py test productos -v 2`
6. `python manage.py runserver 127.0.0.1:8001`
7. Desde la carpeta superior: `python -B -m unittest -v test_operaciones_stock`.

Para registrar un producto usar `POST /api/productos/` con autorización administrativa, JSON: `id` entero, `nombre`, `descripcion`, `precio` entero positivo en CLP, `categoria`, `stock_inicial` entero >= 0 e `imagenes` con 4–6 URL. El servicio almacena `stock.reservado=0`, `stock.disponible=stock_inicial`, `activo=true`.

## Dependencias, seguridad y riesgos pendientes
- **Índice MongoDB único en `productos.id`**: indispensable frente a inserciones concurrentes (verificar ejecución de `indices.js` de infraestructura de James). Una consulta previa no evita una carrera.
- **Replica set MongoDB inicializado y accesible**: verificar que `with_transaction` realmente confirme, revierta y proteja las reservas. Los mocks no lo prueban.
- **Autenticación definitiva**: sustituir tokens compartidos provisionales por verificación de token/roles con el escuadrón Gestión; no declarar segura la API para producción.
- **Vencimiento y conciliación**: acordar con Comercio quién autoriza consolidar/liberar y cómo conciliar pagos; el token temporal por sí solo no prueba el estado de pago.
- **Imágenes**: los registros iniciales de James no contienen `imagenes`; coordinar contrato para que nuevos productos guarden URLs. Los anteriores siguen consultables sin ese campo.
- **Persistencia y despliegue**: verificar conexión real, índice único, reinicio con datos persistentes, variables/secretos fuera del repo y receta reproducible desde clon limpio.
- **Script de seed**: `poblar_bd.js` ejecuta `db.productos.drop()`; NO correrlo en una BD con datos que deban conservarse.

## Evidencias para Sprint Review
Guardar captura de: resultados de pruebas Django, inventario, rutas Django, `git log` con contribuciones propias, ramas/remoto, contrato API y respuesta HTTP de endpoints. La prueba de persistencia MongoDB real y las autorizaciones de Gestión requieren coordinación del equipo.

**Nota**: la entrega de código y pruebas aisladas no equivale a una integración completa o validada en producción.
