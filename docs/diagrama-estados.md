\*\*3. docs/diagrama-estados.md\*\*

Este archivo crea e incluye el diagrama Mermaid: 



```markdown

\# Diagrama de Estados de la Orden



```mermaid

stateDiagram-v2

&#x20;   \[\*] --> PENDIENTE\_PAGO : Crear Orden

&#x20;   

&#x20;   PENDIENTE\_PAGO --> RECHAZADA : Pago Fallido

&#x20;   PENDIENTE\_PAGO --> CONFIRMACION\_PENDIENTE : Pago Aprobado

&#x20;   PENDIENTE\_PAGO --> VENCIDA : Tiempo agotado

&#x20;   PENDIENTE\_PAGO --> CANCELADA : Cancelación de usuario

&#x20;   

&#x20;   CONFIRMACION\_PENDIENTE --> CONFIRMADA : Inventario consolidado

&#x20;   CONFIRMACION\_PENDIENTE --> REVISION\_REQUERIDA : Fallo en consolidación

&#x20;   

&#x20;   REVISION\_REQUERIDA --> CONFIRMADA : Conciliación exitosa

&#x20;   REVISION\_REQUERIDA --> CANCELADA : Conciliación fallida

&#x20;   

&#x20;   RECHAZADA --> \[\*]

&#x20;   CONFIRMADA --> \[\*]

&#x20;   VENCIDA --> \[\*]

&#x20;   CANCELADA --> \[\*]

