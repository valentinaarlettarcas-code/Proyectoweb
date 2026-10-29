import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';

function DetalleProducto() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [cantidad, setCantidad] = useState(1);
  const [imagenActiva, setImagenActiva] = useState(0);

  // Mock de producto (cuando Catalogo este listo, se reemplaza por fetch)
  const productosMock = {
    1: {
      id: 1,
      nombre: 'Teclado Mecánico RGB',
      precio: 30000,
      stock: 10,
      categoria: 'Teclados',
      descripcion: 'Teclado mecánico con switches azules, retroiluminación RGB personalizable y estructura de aluminio. Incluye wrist rest magnético.',
      imagenes: ['Vista frontal', 'Vista lateral', 'Detalle switches', 'Retroiluminación', 'Wrist rest']
    },
    2: {
      id: 2,
      nombre: 'Mouse Gaming Pro',
      precio: 18000,
      stock: 15,
      categoria: 'Mouse',
      descripcion: 'Mouse con sensor óptico de 16000 DPI, 7 botones programables y peso ajustable. Ideal para FPS.',
      imagenes: ['Vista superior', 'Vista lateral', 'Cable trenzado', 'Peso ajustable']
    },
    3: {
      id: 3,
      nombre: 'Auriculares Surround 7.1',
      precio: 45000,
      stock: 5,
      categoria: 'Auriculares',
      descripcion: 'Auriculares con sonido surround virtual 7.1, micrófono desmontable con cancelación de ruido y diadema acolchada.',
      imagenes: ['Frontal', 'Lateral', 'Micrófono', 'Diadema', 'Conector']
    },
  };

  const producto = productosMock[id] || {
    id,
    nombre: 'Producto no encontrado',
    precio: 0,
    stock: 0,
    categoria: '—',
    descripcion: 'El producto no existe o fue dado de baja.',
    imagenes: ['Sin imagen']
  };

  const agotado = producto.stock === 0;

  const handleAgregarCarrito = () => {
    if (agotado) return;
    // PENDIENTE: llamar al backend para agregar al carrito
    alert(`Agregaste ${cantidad} unidad(es) de ${producto.nombre} al carrito`);
    navigate('/carrito');
  };

  return (
    <div className="contenedor">
      <Link to="/catalogo" className="texto-secundario">‹ Volver al catálogo</Link>

      <div className="detalle-producto margin-top">
        {/* Galería */}
        <div className="detalle-producto-galeria">
          <div className="detalle-producto-galeria-imagen-principal">
            [Imagen {producto.imagenes[imagenActiva]}]
          </div>
          <div className="detalle-producto-galeria-miniaturas">
            {producto.imagenes.map((img, i) => (
              <button
                key={i}
                onClick={() => setImagenActiva(i)}
                className={`detalle-producto-miniatura ${i === imagenActiva ? 'detalle-producto-miniatura-activa' : ''}`}
                aria-label={`Ver imagen ${i + 1}`}
              />
            ))}
          </div>
          <p className="texto-secundario" style={{ fontSize: '12px', marginTop: '4px' }}>
            {imagenActiva + 1} / {producto.imagenes.length}
          </p>
        </div>

        {/* Info */}
        <div className="detalle-producto-info">
          <span className="badge-categoria">{producto.categoria}</span>
          <h1>{producto.nombre}</h1>
          <p className="detalle-producto-precio">${producto.precio.toLocaleString('es-CL')} CLP</p>
          <p className="detalle-producto-descripcion">{producto.descripcion}</p>

          {agotado ? (
            <p className="producto-stock-agotado" style={{ marginBottom: '20px' }}>Producto agotado</p>
          ) : (
            <p className="producto-stock-disponible" style={{ marginBottom: '20px' }}>
              {producto.stock} unidades disponibles
            </p>
          )}

          <div className="detalle-producto-cantidad">
            <label>Cantidad:</label>
            <input
              type="number"
              min="1"
              max={producto.stock || 1}
              value={cantidad}
              onChange={(e) => setCantidad(Math.max(1, parseInt(e.target.value) || 1))}
              disabled={agotado}
            />
          </div>

          <button
            onClick={handleAgregarCarrito}
            disabled={agotado}
            className="boton boton-primario"
          >
            {agotado ? 'No disponible' : 'Agregar al carrito'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default DetalleProducto;