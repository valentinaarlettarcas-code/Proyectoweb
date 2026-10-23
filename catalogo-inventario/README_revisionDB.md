# Avance 3: Infraestructura de Base de Datos y Catálogo

En este avance logramos configurar la infraestructura de la base de datos y validar todas las reglas de negocio exigidas para el catálogo de productos (paginación, filtros y control de stock).

## Lo que se cumplió en este avance
1. **Infraestructura con Replica Set:** Configuramos MongoDB usando Docker Compose con 3 nodos. Activamos el Replica Set (`rs_catalogo`) para poder soportar transacciones multidocumento, lo cual probamos con éxito en el nodo primario.
2. **Modelo de datos:** Poblamos la base de datos `catalogo_db` respetando el esquema definido en `modelo_producto.json`, donde el stock se maneja con el formato `{reservado, disponible}` y el estado del producto es un booleano (`activo`).
3. **Lógica del catálogo público:** Construimos una consulta (Aggregation Pipeline) que demuestra que la base de datos ya es capaz de traer un máximo de 50 productos, filtrar solo los que están activos y detectar dinámicamente cuáles están "agotados" si su stock disponible llega a 0.

## Pasos para ejecutar y probar el proyecto
Para revisar este avance a nivel local, se deben seguir estos pasos en la terminal:

1. Levantar los contenedores de la base de datos:
   docker-compose up -d

2. Entrar al nodo principal (Primary) especificando su puerto:
   docker exec -it mongo_catalogo_3 mongosh --port 27019

3. Cambiar a la base de datos del proyecto:
   use catalogo_db

4. Cargar los datos de prueba ejecutando el código del script `poblar_bd.js`.

5. Para verificar el funcionamiento de las reglas del catálogo, pegar esta consulta en la consola de Mongo. Esto aplicará los filtros, la paginación de 50 ítems y creará el campo de "agotado" al vuelo:

   db.productos.aggregate([
     { $match: { activo: true } },
     { $addFields: { 
         agotado: { $eq: ["$stock.disponible", 0] },
         galeria: { $ifNull: ["$galeria", ["imagen_frontal.jpg", "imagen_lateral.jpg"]] } 
     }},
     { $limit: 50 }
   ])

## Decisión de Arquitectura para Producción
Para el entorno en la nube, hemos decidido utilizar **MongoDB Atlas (Clúster M0 - Free Tier)**. 

La razón técnica principal es que este plan gratuito levanta automáticamente la base de datos como un 
Replica Set.Esto nos asegura que las transacciones multidocumento funcionarán de forma nativa
en la nube, ahorrándonos el problema de tener que configurar y mantener nodos de Docker manualmente en un VPS.