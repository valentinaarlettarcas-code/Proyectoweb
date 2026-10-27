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
    <div style={{ padding: '20px' }}>
      <h1>Checkout / Pago</h1>
      <p>El backend valida el carrito y crea la orden. Luego inicias el pago en Transbank.</p>

      {error && (
        <div style={{ padding: '10px', backgroundColor: '#fee', border: '1px solid #c33', margin: '10px 0' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      <button
        onClick={handlePagar}
        disabled={cargando}
        style={{
          marginTop: '20px',
          padding: '10px 20px',
          cursor: cargando ? 'not-allowed' : 'pointer',
          opacity: cargando ? 0.6 : 1,
        }}
      >
        {cargando ? 'Procesando...' : 'Pagar con Webpay (Sandbox)'}
      </button>
    </div>
  );
}

export default Checkout;