\# Contrato de API - Servicio Comercio



\## Autenticación

Todos los endpoints requieren el header: `Authorization: Token <token>`. El token se valida internamente contra el servicio de Gestión exigiendo rol de CLIENTE y cuenta en estado ACTIVO.



\### Crear Orden (`POST /api/ordenes/`)

\- \*\*Descripción:\*\* Crea una nueva orden. El cliente solo envía el producto y la cantidad; el backend calcula precios, subtotales y el total consultando internamente.

\- \*\*Repetición segura:\*\* Enviar un `checkout\_id` existente para un mismo cliente retorna la orden previamente creada (200 OK) en lugar de duplicarla.

\- \*\*Request Body:\*\*

&#x20; ```json

&#x20; {

&#x20;   "checkout\_id": "string",

&#x20;   "items": \[

&#x20;     {

&#x20;       "producto\_id": "string",

&#x20;       "quantity": 1

&#x20;     }

&#x20;   ]

&#x20; }

