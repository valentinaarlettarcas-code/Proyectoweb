import { useState } from 'react';
import { crearOrdenPrueba, iniciarPago } from '../servicios/ServicioDev';
function Checkout() {
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);
  const [log, setLog] = useState([]);

  const agregarLog = (msg) => {
    setLog((prev) => [...prev, msg]);
  };

  const handlePagar = async () => {
    if (cargando) return;
    setCargando(true);
    setError(null);
    setLog([]);
    try {
      agregarLog('1. Creando orden de prueba en backend...');
      const orden = await crearOrdenPrueba('dev-001');
      agregarLog(`   Orden creada: id=${orden.id}, total=${orden.total_amount} ${orden.moneda}`);

      agregarLog('2. Solicitando intento de pago a Transbank...');
      const returnUrl = `${window.location.origin}/pago/retorno`;
      const intento = await iniciarPago(orden.id, returnUrl);
      agregarLog(`   Intento creado: buy_order=${intento.buy_order}`);
      agregarLog(`   Monto: ${intento.amount} ${intento.currency}`);
      agregarLog('3. Redirigiendo a Transbank...');

      if (intento.checkout_url) {
        // Pequeno delay para que se vea el log antes de redirigir
        setTimeout(() => {
          window.location.href = intento.checkout_url;
        }, 1500);
      } else {
        throw new Error('El backend no devolvio una URL de pago.');
      }
    } catch (err) {
      setError(err.message);
      setCargando(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '700px' }}>
      <h1>Checkout / Pago</h1>
      <p>El backend valida el carrito y crea la orden. Luego inicias el pago en Transbank.</p>

      {error && (
        <div style={{ padding: '10px', backgroundColor: '#fee', border: '1px solid #c33', margin: '10px 0' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {log.length > 0 && (
        <div style={{ padding: '10px', backgroundColor: '#f4f4f4', border: '1px solid #ccc', margin: '10px 0', fontFamily: 'monospace' }}>
          {log.map((linea, i) => (
            <div key={i}>{linea}</div>
          ))}
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