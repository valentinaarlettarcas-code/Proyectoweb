import { useSearchParams, Link } from 'react-router-dom';

function RetornoPago() {
  const [params] = useSearchParams();
  const tokenWs = params.get('token_ws');
  const tbkToken = params.get('TBK_TOKEN');
  const tbkOrden = params.get('TBK_ORDEN_COMPRA');
  const abandono = tbkToken && !tokenWs;

  return (
    <div className="contenedor" style={{ maxWidth: '600px' }}>
      <h1 style={{ marginBottom: '20px' }}>Retorno de pago</h1>

      {abandono && (
        <div className="mensaje-error">
          <strong>Pago abandonado o cancelado.</strong>
          <p style={{ marginTop: '6px' }}>La orden no fue confirmada. Puedes reintentar.</p>
          {tbkOrden && <p style={{ marginTop: '6px' }}>Orden: {tbkOrden}</p>}
        </div>
      )}

      {tokenWs && (
        <div className="mensaje-exito">
          <strong>Token recibido de Transbank:</strong>
          <p style={{ marginTop: '6px', wordBreak: 'break-all' }}>{tokenWs}</p>
          <p style={{ marginTop: '8px', fontSize: '13px' }}>
            H3 implementará la verificación enviando este token al backend.
          </p>
        </div>
      )}

      {!tokenWs && !abandono && (
        <p className="texto-secundario">Llegaste aquí sin un token válido.</p>
      )}

      <div className="margin-top">
        <Link to="/carrito" className="boton boton-secundario">Volver al carrito</Link>
      </div>
    </div>
  );
}

export default RetornoPago;