import { Link } from 'react-router-dom';

function Carrito() {
  // Mock de productos del carrito
  const items = [
    { id: 1, nombre: 'Teclado Mecánico RGB', precio: 30000, cantidad: 1 },
  ];
  const total = items.reduce((sum, i) => sum + i.precio * i.cantidad, 0);

  return (
    <div className="contenedor">
      <h1 style={{ marginBottom: '20px' }}>Carrito de compras</h1>

      {items.length === 0 ? (
        <p className="texto-secundario texto-centrado" style={{ padding: '40px' }}>
          Tu carrito está vacío.
        </p>
      ) : (
        <>
          {items.map((item) => (
            <div key={item.id} className="tarjeta" style={{ marginBottom: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h3 className="producto-nombre">{item.nombre}</h3>
                <p className="texto-secundario">Cantidad: {item.cantidad}</p>
              </div>
              <p className="producto-precio">${(item.precio * item.cantidad).toLocaleString('es-CL')} CLP</p>
            </div>
          ))}

          <div className="tarjeta" style={{ marginTop: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <strong>Total:</strong>
            <p className="producto-precio" style={{ fontSize: '20px' }}>${total.toLocaleString('es-CL')} CLP</p>
          </div>

          <div style={{ marginTop: '20px' }}>
            <Link to="/checkout" className="boton boton-primario">Ir a pagar</Link>
          </div>
        </>
      )}
    </div>
  );
}

export default Carrito;