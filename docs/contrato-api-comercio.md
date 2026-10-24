\# Contrato de API -Servicio Comercio



\## Autenticación

Todos los endpoints requieren el header: `Authorization: Token <token>`. El token se valida internamente contra el servicio de Gestión exigiendo rol de CLIENTE y cuenta en estado ACTIVO.



\## Endpoints



\### Crear Orden (`POST /api/orders/`)

\- \*\*Repetición segura:\*\* Enviar un `checkout\_id` existente para un mismo cliente retorna la orden previamente creada (200 OK) en lugar de duplicarla.

\- \*\*Request Body:\*\*

&#x20; ```json

&#x20; {

&#x20;   "checkout\_id": "string",

&#x20;   "total\_amount": 0,

&#x20;   "moneda": "CLP",

&#x20;   "items": \[

&#x20;     {

&#x20;       "producto\_id": "string",

&#x20;       "historical\_product\_name": "string",

&#x20;       "historical\_price": 1000,

&#x20;       "moneda": "CLP",

&#x20;       "quantity": 1

&#x20;     }

&#x20;   ]

&#x20; }

