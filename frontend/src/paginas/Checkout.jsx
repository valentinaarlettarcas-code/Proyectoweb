import { Link } from 'react-router-dom';
function Checkout() {
    return (
        <div>
            <h1>Checkout / Pago</h1>
            <p>Aqui el backend debe validar el carrito y crear la orden pendiente.</p>
            <button>Pagar con Webpay (Sandbox)</button>
        </div>
    );
}

export default Checkout;


