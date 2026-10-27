
# Catálogo e Inventario — Evidencia de Carlos, Sprint 2

## 1. Entregas propias

- Microservicio de Catálogo desarrollado con Django REST Framework.
- Contrato API para comunicación con el servicio de Comercio.
- Consulta de productos mediante GET.
- Creación inicial de productos mediante POST administrativo.
- Creación de reservas de stock.
- Consolidación de reservas después de una confirmación de pago.
- Liberación de reservas por rechazo, cancelación o vencimiento.
- Validaciones de productos y operaciones de inventario.
- Pruebas unitarias e HTTP con dependencias simuladas.

## 2. Estructura del microservicio

Los archivos de stock están ubicados dentro de `servicio_catalogo`.

```text
catalogo-inventario/
└── servicio_catalogo/
    ├── manage.py
    ├── operaciones_stock.py
    ├── reservas_stock.py
    ├── test_operaciones_stock.py
    ├── VERIFICAR_SPRINT2.ps1
    ├── README_CIERRE_SPRINT2.md
    ├── config/
    └── productos/
```

Los archivos ya no se mantienen duplicados en la carpeta exterior `catalogo-inventario/`.

Las vistas de Django importan los módulos desde `servicio_catalogo`.

## 3. Contrato API desarrollado

### GET /api/productos/{id}/

Permite consultar información de un producto.

### POST /api/productos/

Permite crear un producto mediante autorización administrativa provisional.

### POST /api/reservas/

Permite crear una reserva de inventario.

### POST /api/reservas/{id}/consolidar/

Permite consolidar una reserva previamente creada.

### POST /api/reservas/{id}/liberar/

Permite liberar una reserva por un motivo permitido.

Las rutas y los campos utilizados por Comercio deben mantenerse compatibles.

Cualquier modificación del contrato compartido debe coordinarse previamente con Matías.

## 4. Creación inicial de productos

La implementación inicial de HU-08 incorpora validaciones para:

- ID entero.
- Nombre del producto.
- Descripción.
- Precio numérico positivo y finito.
- Categoría.
- Stock inicial entero no negativo.
- Entre 4 y 6 imágenes.

El modelo de stock utiliza:

- `stock.disponible`
- `stock.reservado`

La persistencia completa de las imágenes, sus textos alternativos y las operaciones administrativas adicionales deben verificarse como parte del sprint actual.

## 5. Preparación del entorno

Utilizar Python y un entorno virtual con las dependencias de Django, Django REST Framework y PyMongo.

El entorno empleado durante las pruebas fue:

- Python 3.14.7.
- Django 6.1.2.
- PyMongo 4.18.3.

### Variables de entorno

El proyecto utiliza las siguientes variables:

**DJANGO_SECRET_KEY**

Clave secreta utilizada por Django.

**CATALOGO_MONGO_URI**

URI de conexión a MongoDB, necesaria para operaciones reales de lectura y escritura.

**CATALOGO_INTERNAL_TOKEN**

Token interno provisional para llamadas desde otros servicios.

**CATALOGO_ADMIN_TOKEN**

Token administrativo provisional de desarrollo.

**CATALOGO_PYTHON**

Variable opcional utilizada por el script de verificación para seleccionar el intérprete de Python.

No guardar contraseñas, tokens ni secretos reales en Git.

## 6. Ejecutar comprobaciones desde servicio_catalogo

Ubicarse en la carpeta que contiene `manage.py`:

```text
catalogo-inventario/servicio_catalogo/
```

### Comprobación de Django

```powershell
python manage.py check
```

### Pruebas Django

```powershell
python manage.py test productos -v 2
```

### Pruebas de inventario

```powershell
python -B -m unittest -v test_operaciones_stock
```

**Importante:** las pruebas de inventario se ejecutan desde `servicio_catalogo`, no desde la carpeta superior.

## 7. Verificación automatizada

El archivo `VERIFICAR_SPRINT2.ps1` permite ejecutar las comprobaciones anteriores desde PowerShell.

Comando:

```powershell
.\VERIFICAR_SPRINT2.ps1
```

El script:

1. Comprueba la configuración de Django.
2. Ejecuta las pruebas HTTP y las validaciones.
3. Ejecuta las pruebas de inventario.
4. Comprueba la resolución de las rutas Django.
5. Muestra la rama activa de Git.
6. Muestra los archivos modificados.
7. Muestra los últimos commits.
8. Presenta el resumen de resultados.

El script debe finalizar con error cuando alguna comprobación falle.

### Selección del entorno Python

Para utilizar el entorno virtual `catalogo-web`:

```powershell
$env:CATALOGO_PYTHON = "$HOME\.venvs\catalogo-web\Scripts\python.exe"
```

Para configurar temporalmente la clave de Django:

```powershell
$env:DJANGO_SECRET_KEY = (
    [guid]::NewGuid().ToString("N") +
    [guid]::NewGuid().ToString("N")
)
```

Después, ejecutar:

```powershell
.\VERIFICAR_SPRINT2.ps1
```

## 8. Resultados de referencia

Tras la reorganización de los módulos se obtuvieron:

- Django check: 0 problemas.
- Pruebas Django: 43 de 43 aprobadas.
- Pruebas de inventario: 19 de 19 aprobadas.

**Total: 62 pruebas automatizadas aprobadas.**

Estas pruebas utilizan simulaciones y no demuestran por sí solas el funcionamiento de MongoDB remoto.

## 9. Dependencias y riesgos pendientes

### MongoDB

Verificar la conexión real, los índices únicos y las operaciones transaccionales con un replica set compatible.

### Reservas

Comprobar que la consolidación y liberación mantengan la integridad del stock bajo operaciones concurrentes.

### Autenticación

La autenticación actual mediante tokens es provisional.

Su sustitución por la autenticación definitiva debe coordinarse con el equipo correspondiente.

### Imágenes

Revisar la persistencia real de las imágenes de producto, su cantidad permitida y el texto alternativo obligatorio.

### Administración de productos

Completar y comprobar las operaciones de:

- Listar productos.
- Consultar productos para administración.
- Editar productos existentes.
- Desactivar productos sin eliminarlos físicamente.

### RF19 — Ajuste de existencias

Implementar el ajuste de existencias con:

- Validación de cantidades.
- Control de concurrencia.
- Registro persistente del administrador responsable.
- Fecha y hora del ajuste.
- Valor anterior de las existencias.
- Valor nuevo de las existencias.

El ajuste no debe dejar el stock físico por debajo de las unidades reservadas.

### Integración con Comercio

No modificar rutas, campos o estructuras de respuesta compartidas sin coordinación previa con Matías.

### Script de datos iniciales

El archivo `poblar_bd.js` puede eliminar datos existentes si contiene una operación `drop()`.

No ejecutarlo sobre una base de datos que contenga información que deba conservarse.

## 10. Evidencias para Sprint Review

Se recomienda conservar evidencia de:

- Comprobación Django sin errores.
- Resultado de las pruebas Django.
- Resultado de las pruebas de inventario.
- Resolución de rutas HTTP.
- Rama Git y commits propios.
- Contrato de la API.
- Respuestas HTTP de los endpoints.
- Validaciones y tratamiento de errores.

## 11. Organización del trabajo

El desarrollo de Carlos se mantiene en una rama propia de Git.

El objetivo es utilizar el nombre:

```text
feature/catalogo-inventario-diseno
```

Los cambios deben registrarse mediante commits descriptivos.

No se deben incorporar archivos auxiliares de otros integrantes sin coordinación previa.

Los cambios del contrato compartido con Comercio requieren comunicación con Matías.

## 12. Observación final

La aprobación de las pruebas unitarias y HTTP no equivale a una integración completa ni a una validación en producción.

La persistencia en MongoDB, la seguridad definitiva y la comunicación real entre microservicios requieren pruebas adicionales del equipo.

Este documento registra el estado técnico del Sprint 2 y las verificaciones realizadas durante la reorganización de los módulos de Catálogo e Inventario.

Los requisitos administrativos RF17, RF18 y RF19 forman parte de las actividades pendientes del sprint actual.
