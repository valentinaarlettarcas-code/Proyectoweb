import { useSearchParams, Link } from 'react-router-dom';

function RetornoPago() {
  const [params] = useSearchParams();
  const tokenWs = params.get('token_ws');
  const tbkToken = params.get('TBK_TOKEN');
  const tbkOrden = params.get('TBK_ORDEN_COMPRA');
  const abandono = tbkToken && !tokenWs;

  return (
    <div style={{ padding: '20px' }}>
      <h1>Retorno de pago</h1>

      {abandono && (
        <div style={{ padding: '10px', backgroundColor: '#fee', border: '1px solid #c33', margin: '10px 0' }}>
          <strong>Pago abandonado o cancelado.</strong>
          <p>La orden no fue confirmada. Puedes reintentar.</p>
          {tbkOrden && <p>Orden: {tbkOrden}</p>}
        </div>
      )}

      {tokenWs && (
        <div style={{ padding: '10px', backgroundColor: '#efe', border: '1px solid #3c3', margin: '10px 0' }}>
          <strong>Token recibido de Transbank:</strong>
          <p style={{ wordBreak: 'break-all' }}>{tokenWs}</p>
          <p><small>H3 implementara la verificacion enviando este token al backend.</small></p>
        </div>
      )}

      {!tokenWs && !abandono && <p>Llegaste aqui sin token valido.</p>}

      <div style={{ marginTop: '20px' }}>
        <Link to="/carrito">
          <button style={{ padding: '10px 20px', cursor: 'pointer' }}>Volver al carrito</button>
        </Link>
      </div>
    </div>
  );
}

export default RetornoPago;
