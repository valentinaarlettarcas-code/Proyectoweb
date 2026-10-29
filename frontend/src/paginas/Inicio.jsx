import { Link } from 'react-router-dom';

function Inicio() {
  const categorias = [
    { nombre: 'Teclados', icono: '⌨️' },
    { nombre: 'Mouse', icono: '🖱️' },
    { nombre: 'Auriculares', icono: '🎧' },
    { nombre: 'Monitores', icono: '🖥️' },
  ];

  const destacados = [
    { id: 1, nombre: 'Teclado Mecánico RGB', precio: 30000 },
    { id: 2, nombre: 'Mouse Gaming Pro', precio: 18000 },
    { id: 3, nombre: 'Auriculares Surround', precio: 45000 },
    { id: 4, nombre: 'Mousepad XL', precio: 12000 },
  ];

  return (
    <div className="contenedor">
      <section className="hero">
        <h1>
          Bienvenido a <span style={{ color: 'var(--color-texto)' }}>SETUP</span>
          <span style={{ color: 'var(--color-primario)' }}>VERSE</span>
        </h1>
        <p>Accesorios tech y gaming para armar tu setup perfecto</p>
        <Link to="/catalogo" className="boton boton-primario">Ver catálogo</Link>
      </section>

      <section className="seccion">
        <h2>Categorías</h2>
        <div className="grilla-categorias">
          {categorias.map((cat) => (
            <Link key={cat.nombre} to="/catalogo" className="tarjeta texto-centrado">
              <div style={{ fontSize: '40px', marginBottom: '10px' }}>{cat.icono}</div>
              <div>{cat.nombre}</div>
            </Link>
          ))}
        </div>
      </section>

      <section className="seccion">
        <h2>Productos destacados</h2>
        <div className="grilla">
          {destacados.map((p) => (
            <Link key={p.id} to={`/catalogo/${p.id}`} className="tarjeta">
              <div className="imagen-placeholder">[Imagen]</div>
              <h3 className="producto-nombre">{p.nombre}</h3>
              <p className="producto-precio">${p.precio.toLocaleString('es-CL')} CLP</p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}

export default Inicio;