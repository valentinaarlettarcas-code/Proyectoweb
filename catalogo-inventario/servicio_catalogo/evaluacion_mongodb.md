# Evaluación de Persistencia Remota: MongoDB Atlas

Para el entorno de producción/pruebas remotas del microservicio de Catálogo e Inventario, se evaluó la opción de MongoDB Atlas utilizando su capa gratuita (Clúster M0).

## 1. Soporte para Transacciones Multidocumento
**SÍ está soportado.**
Las transacciones ACID multidocumento requieren que la base de datos se despliegue como un *Replica Set*.
Todos los clústeres M0 gratuitos de MongoDB Atlas se instalan automáticamente bajo una arquitectura de Replica Set (1 nodo primario y 2 secundarios).
Por lo tanto, las funciones que utilizan `with_transaction()` operarán de forma nativa sin generar errores.


## 2. Revisión de Cuotas y Condiciones (Capa M0 Free)

Es importante destacar que el servicio es 100% gratuito y no requiere tarjeta de crédito, pero 
impone los siguientes límites que debemos respetar en el código:

* **Almacenamiento:** Límite estricto de 512 MB.
  
* **Conexiones Concurrentes:** Máximo 500 conexiones simultáneas.
  
* **Operaciones (Rendimiento):** Limitado a 100 operaciones por segundo.
  
* **Inactividad:** Si el clúster no recibe conexiones en un período de 7 días consecutivos, se pausará automáticamente.
  
* **Respaldos:** No incluye copias de seguridad automatizadas de la base de datos.
  
