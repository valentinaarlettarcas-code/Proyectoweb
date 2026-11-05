# Contenidos editables de SetupVerse

El administrador edita los contenidos de las páginas públicas sin cambiar código. Los cambios válidos se guardan y se publican de inmediato.

## Páginas
- `inicio`
- `contacto`
- `quienes-somos`

## Tipos de bloque y campos obligatorios

| Tipo | Obligatorios | Opcionales | Uso |
|---|---|---|---|
| texto | cuerpo | titulo | Párrafos y títulos |
| imagen | imagen_url, texto_alternativo | | Imágenes de la página |
| enlace | titulo, enlace_url | | Botones y enlaces |
| banner | titulo, imagen_url, texto_alternativo | cuerpo, enlace_url | Banners destacados |

## Validaciones
- `clave`: letras, números, guiones y guiones bajos, hasta 50 caracteres. Es única dentro de cada página.
- `titulo`: hasta 200 caracteres. `cuerpo`: hasta 2.000. `texto_alternativo`: hasta 200.
- `imagen_url` y `enlace_url`: una URL http(s) válida o una ruta interna que empiece con `/`. Se rechazan otros esquemas (por ejemplo `javascript:`) y las rutas que empiezan con `//`.
- `orden`: número entero positivo; define el orden dentro de la página.
- `activo`: un bloque inactivo no se muestra en el sitio público.
- Una edición inválida se rechaza completa y conserva los valores anteriores.

## API
- Público, sin sesión: `GET /api/contenidos/publico/<pagina>/`. Devuelve los bloques activos ordenados, sin campos internos. Una página inexistente responde 404.
- Administración (solo administrador activo): `GET` y `POST /api/contenidos/` (filtro opcional `?pagina=`), y `GET`, `PUT`, `PATCH` y `DELETE /api/contenidos/<id>/`.