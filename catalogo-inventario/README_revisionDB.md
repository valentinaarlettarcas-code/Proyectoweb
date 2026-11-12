# Avance 3: Infraestructura de Base de Datos y Catálogo

En este avance logramos configurar la infraestructura de la base de datos y validar todas las reglas de negocio exigidas para el catálogo de productos (paginación, filtros y control de stock).

## Lo que se cumplió en este avance

- **Infraestructura con Replica Set:** Configuramos MongoDB usando Docker Compose con 3 nodos. Activamos el Replica Set (`rs_catalogo`) para soportar transacciones multidocumento en reservas de stock.
- **Modelo de datos:** Poblamos la base de datos `catalogo_db` respetando el esquema definido en `modelo_producto.json`, donde el stock se maneja con el formato `{reservado, disponible}` y el estado del producto es un booleano (`activo`).
- **Lógica del catálogo público:** Construimos una consulta (Aggregation Pipeline) que demuestra que la base de datos filtra productos activos, aplica paginación de hasta 50 productos y detecta dinámicamente cuáles están agotados si su stock disponible llega a `0`.

## Pasos para ejecutar y probar el proyecto en desarrollo local

> **Advertencia:** El archivo `docker-compose.yml` de esta carpeta es **exclusivamente para desarrollo local**. No tiene autenticación configurada y publica los puertos (`27027`, `27028`, `27029`) en el equipo anfitrión.

Para revisar este avance desde un clon limpio, ejecutar los siguientes pasos desde `catalogo-inventario/`:

1. **Levantar los tres contenedores de MongoDB:**

       docker compose up -d

2. **Inicializar el Replica Set `rs_catalogo`** (el `docker-compose.yml` solo levanta los nodos y no ejecuta la inicialización automáticamente; este paso es obligatorio para que funcionen las transacciones de reserva):

       docker exec -it mongo_catalogo_1 mongosh --eval "rs.initiate({_id: 'rs_catalogo', members: [{_id: 0, host: 'mongo1:27017'}, {_id: 1, host: 'mongo2:27018'}, {_id: 2, host: 'mongo3:27019'}]})"

   *(Se puede verificar que quedó activo un nodo `PRIMARY` y dos `SECONDARY` ejecutando `docker exec -it mongo_catalogo_1 mongosh --eval "rs.status()"`).*

3. **Crear los índices y cargar los datos iniciales con sus imágenes:**

       docker exec -i mongo_catalogo_1 mongosh < indices.js
       docker exec -i mongo_catalogo_1 mongosh < poblar_bd.js

   *(Nota: Si el nodo primario elegido fue `mongo_catalogo_2` en puerto `27018` o `mongo_catalogo_3` en puerto `27019`, ejecutar `mongosh --port 27018` o `mongosh --port 27019` según corresponda).*

4. **Verificar el funcionamiento de las reglas del catálogo en consola:**
   Entrar a `mongosh` en el nodo primario, seleccionar `use catalogo_db` y ejecutar:

       db.productos.aggregate([
         { $match: { activo: true } },
         { $addFields: {
           agotado: { $eq: ["$stock.disponible", 0] },
           galeria: { $ifNull: ["$galeria", ["imagen_frontal.jpg", "imagen_lateral.jpg"]] }
         }},
         { $limit: 50 }
       ])

## Conexión para Integración con Otros Módulos

Para que otros módulos se conecten a esta base de datos en desarrollo local, configurar en el archivo `.env`:

- **Si el backend corre directamente en el sistema operativo (fuera de Docker):**

      CATALOGO_MONGO_URI="mongodb://localhost:27027,localhost:27028,localhost:27029/catalogo_db?replicaSet=rs_catalogo"

- **Si el backend corre dentro de un contenedor Docker compartiendo la misma red:**

      CATALOGO_MONGO_URI="mongodb://mongo1:27017,mongo2:27018,mongo3:27019/catalogo_db?replicaSet=rs_catalogo"

## Decisión de Arquitectura para Producción

Para el entorno en la nube, hemos decidido utilizar **MongoDB Atlas (Clúster M0 - Free Tier)**, ya que levanta automáticamente la base de datos como un Replica Set y asegura el soporte nativo de transacciones multidocumento sin tener que administrar nodos Docker manualmente.