
# Wireframes de E-commerce de accesorios tech y gaming

## Objetivo

Definir la estructura visual y navegación propuestas para cinco pantallas:

1. Autenticación.
2. Registro de usuario.
3. Carrito de compras.
4. Pago.
5. Resumen y confirmación.

Estos wireframes son bocetos de diseño y no representan pantallas funcionales.

## Archivo visual

Los cinco diseños están disponibles en [wireframes.html](wireframes.html).

El archivo se puede abrir directamente en el navegador para revisar las pantallas o imprimirlas como PDF.

## 1. Autenticación

### Elementos

- Identificación de E-commerce de accesorios tech y gaming.
- Campo de correo electrónico.
- Campo de contraseña.
- Botón de inicio de sesión.
- Enlace para crear cuenta.
- Enlace para recuperar contraseña.

### Validaciones

- Correo y contraseña obligatorios.
- Formato correcto del correo.
- Mensaje genérico cuando las credenciales sean incorrectas.

### Navegación

Tras iniciar sesión correctamente, el usuario accede a la aplicación. También puede ir al registro o recuperar su contraseña.

## 2. Registro de usuario

### Elementos

- Nombre.
- Apellido.
- Correo electrónico.
- Contraseña.
- Confirmación de contraseña.
- Botón de registro.
- Enlace al inicio de sesión.

### Validaciones

- Todos los campos obligatorios.
- Correo válido y no duplicado.
- Contraseñas coincidentes.
- Validación de seguridad de la contraseña en el servidor.
- El registro público no permite asignarse un rol de administrador.

### Navegación

Después del registro, el usuario puede acceder al inicio de sesión o a la pantalla de confirmación correspondiente.

## 3. Carrito de compras

### Elementos

- Listado de productos seleccionados.
- Imagen representativa.
- Nombre del producto.
- Cantidad.
- Precio.
- Opción para eliminar productos.
- Total estimado.
- Botón para continuar al pago.

### Validaciones

- Cantidades positivas.
- Comprobación de disponibilidad.
- Actualización del total al modificar productos.
- Validación definitiva de precios y existencias en el servidor.

### Navegación

El usuario puede continuar comprando o avanzar al pago.

## 4. Pago

### Elementos

- Datos del comprador.
- Método de pago.
- Pasarela de pago segura.
- Total a pagar.
- Botón de confirmación.
- Opción para volver al carrito.

### Validaciones

- Datos obligatorios.
- Disponibilidad de productos.
- Importe definitivo calculado por el backend.
- Comprobación del resultado del pago.

### Navegación

El usuario pasa desde el carrito al proceso de pago y posteriormente al resultado de la operación.

No se deben introducir ni almacenar datos bancarios directamente en estos wireframes.

## 5. Resumen y confirmación

### Elementos

- Mensaje de confirmación.
- Número de pedido.
- Cantidad de productos.
- Importe total.
- Estado del pedido.
- Botón para volver al inicio.

### Validaciones

- Mostrar confirmación únicamente cuando el backend haya confirmado el resultado correspondiente.
- Diferenciar pagos exitosos, pendientes y fallidos.
- Mostrar los datos del pedido registrado.

### Navegación

Tras confirmar el pedido, el usuario puede regresar al inicio de la aplicación.

## Flujo general de navegación

Registro → Autenticación → Carrito → Pago → Confirmación

También se contemplan los siguientes recorridos:

- Autenticación → Recuperar contraseña.
- Carrito → Volver al catálogo.
- Pago → Volver al carrito.
- Pago fallido → Reintentar operación.

## Estado del diseño

Los cinco wireframes constituyen una propuesta visual de E-commerce de accesorios tech y gaming.

Queda pendiente su validación con el equipo y su adaptación a las rutas y componentes definitivos de la aplicación.

