import { useState } from 'react';
import { crearOrden, iniciarPago } from '../servicios/ServicioPago';

function Checkout() {
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  const carritoPrueba = [
    { producto_id: 1, quantity: 1 },
  ];
  const checkoutId = `checkout-${Date.now()}`;

  const handlePagar = async () => {
    if (cargando) return;
    setCargando(true);
    setError(null);
    try {
      const orden = await crearOrden(carritoPrueba, checkoutId);
      const returnUrl = `${window.location.origin}/pago/retorno`;
      const intento = await iniciarPago(orden.id, returnUrl);
      if (intento.checkout_url && intento.token_ws) {
        const urlConToken = `${intento.checkout_url}?token_ws=${intento.token_ws}`;
        window.location.href = urlConToken;
      } else {
        throw new Error('El backend no devolvió una URL de pago válida.');
      }
    } catch (err) {
      setError(err.message);
      setCargando(false);
    }
  };

  return (
    <div className="contenedor" style={{ maxWidth: '600px' }}>
      <h1 style={{ marginBottom: '20px' }}>Checkout / Pago</h1>

      <div className="tarjeta" style={{ marginBottom: '20px' }}>
        <p className="texto-secundario">
          El backend valida el carrito y crea la orden. Luego inicias el pago en Transbank.
        </p>
      </div>

      {error && (
        <div className="mensaje-error">{error}</div>
      )}

      <button
        onClick={handlePagar}
        disabled={cargando}
        className="boton boton-primario"
      >
        {cargando ? 'Procesando...' : 'Pagar con Webpay (Sandbox)'}
      </button>
    </div>
  );
}

export default Checkout;