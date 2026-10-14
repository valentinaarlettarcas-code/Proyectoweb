# Guía de contribución

Reglas de trabajo del equipo para el proyecto de comercio electrónico de accesorios tech y gaming.

## Estructura del repositorio

- `gestion/`: servicio de Gestión (usuarios, roles, contenidos, temas y contacto), con PostgreSQL.
- `catalogo-inventario/`: servicio de Catálogo e Inventario (productos, stock y reservas), con MongoDB.
- `comercio/`: servicio de Comercio (carrito, órdenes, pagos, conciliación y notificaciones).
- `frontend/`: aplicación React con Vite.
- `docs/`: documentación, diagramas y contratos de API.

## Ramas

- `main` es la rama estable. Nadie sube directo a `main`: solo se integra con Pull Request.
- Cada tarea o historia tiene su propia rama, creada desde `main` o desde la rama base que se indique.
- Formato del nombre: `prefijo/descripcion-corta`, en minúsculas, con guiones, sin espacios, sin tildes y sin ñ.
- Prefijos:
  - `feature/` funcionalidad nueva. Ejemplo: `feature/catalogo-modelo-producto`
  - `fix/` corrección de errores. Ejemplo: `fix/bloqueo-ultimo-admin`
  - `docs/` documentación. Ejemplo: `docs/arquitectura-diagramas`
  - `refactor/` cambio interno sin cambiar el comportamiento.
- Las ramas son de vida corta: se integran en pocos días y no acumulan trabajo.

## Commits

- Formato: `tipo: descripción corta`, con un alcance opcional, por ejemplo `feat(comercio): agrega modelo de orden`.
- Tipos: `feat` (funcionalidad nueva), `fix` (corrección), `test` (pruebas), `docs` (documentación), `refactor` (cambio interno), `build` (dependencias y configuración).
- Cada integrante hace sus commits con su propia cuenta de GitHub: las contribuciones se miden por el historial.

## Pull Requests

- Un Pull Request por rama, con el ID de la historia en el título. Ejemplo: `HU-07: Contacto`.
- La descripción indica los requisitos que cubre (RF) y cómo se probó.
- Los tests del servicio deben pasar antes de pedir revisión.
- Lo revisa al menos una persona distinta de quien lo escribió, idealmente de otro escuadrón.
- Se integra solo con aprobación. Nadie integra su propio PR sin revisión.

## Pruebas

- Gestión: desde `gestion/`, `python manage.py test`.
- Todo cambio de lógica incluye sus tests.

## Secretos y configuración

- Nunca se suben contraseñas, tokens, claves ni archivos `.env`.
- Las variables de entorno se documentan sin valores reales.

## Hitos y etiquetas

- Cada hito se entrega con una etiqueta inmutable sobre `main`: `h1`, `h2`, `h3` y `h4`.
- Las etiquetas no se mueven ni se borran.