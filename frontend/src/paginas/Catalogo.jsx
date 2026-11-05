import { useState } from 'react';
import { Link } from 'react-router-dom';

function Catalogo() {
  const [busqueda, setBusqueda] = useState('');
  const [categoria, setCategoria] = useState('todas');
  const [pagina, setPagina] = useState(1);

  // Mock de productos (cuando Catalogo este listo, se reemplaza por fetch)
  const productosMock = [
    { id: 1, nombre: 'Teclado Mecánico RGB', precio: 30000, stock: 10, categoria: 'Teclados' },
    { id: 2, nombre: 'Mouse Gaming Pro', precio: 18000, stock: 15, categoria: 'Mouse' },
    { id: 3, nombre: 'Auriculares Surround 7.1', precio: 45000, stock: 5, categoria: 'Auriculares' },
    { id: 4, nombre: 'Mousepad XL RGB', precio: 12000, stock: 0, categoria: 'Accesorios' },
    { id: 5, nombre: 'Monitor 144Hz 27"', precio: 250000, stock: 3, categoria: 'Monitores' },
    { id: 6, nombre: 'Webcam 4K', precio: 65000, stock: 8, categoria: 'Accesorios' },
    { id: 7, nombre: 'Micrófono Condensador', precio: 55000, stock: 6, categoria: 'Audio' },
    { id: 8, nombre: 'Teclado Tenkeyless', precio: 28000, stock: 12, categoria: 'Teclados' },
    { id: 9, nombre: 'Mouse Inalámbrico', precio: 22000, stock: 20, categoria: 'Mouse' },
    { id: 10, nombre: 'Auriculares In-Ear', precio: 15000, stock: 0, categoria: 'Auriculares' },
    { id: 11, nombre: 'Hub USB-C 7 puertos', precio: 28000, stock: 18, categoria: 'Accesorios' },
    { id: 12, nombre: 'Monitor Ultrawide 34"', precio: 380000, stock: 2, categoria: 'Monitores' },
  ];

  const categorias = ['todas', 'Teclados', 'Mouse', 'Auriculares', 'Monitores', 'Audio', 'Accesorios'];
  const POR_PAGINA = 8;

  let productos = productosMock;
  if (busqueda) {
    productos = productos.filter((p) =>
      p.nombre.toLowerCase().includes(busqueda.toLowerCase())
    );
  }
  if (categoria !== 'todas') {
    productos = productos.filter((p) => p.categoria === categoria);
  }

  const totalPaginas = Math.ceil(productos.length / POR_PAGINA);
  const inicio = (pagina - 1) * POR_PAGINA;
  const productosPagina = productos.slice(inicio, inicio + POR_PAGINA);

  const cambiarBusqueda = (e) => {
    setBusqueda(e.target.value);
    setPagina(1);
  };

  const cambiarCategoria = (c) => {
    setCategoria(c);
    setPagina(1);
  };

  return (
    <div className="contenedor">
      <h1 style={{ marginBottom: '20px' }}>Catálogo</h1>

      <div className="filtros">
        <input
          type="text"
          placeholder="Buscar productos..."
          value={busqueda}
          onChange={cambiarBusqueda}
        />
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {categorias.map((c) => (
            <button
              key={c}
              onClick={() => cambiarCategoria(c)}
              className={`chip-categoria ${categoria === c ? 'chip-categoria-activo' : ''}`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      {productosPagina.length === 0 ? (
        <p className="texto-secundario texto-centrado" style={{ padding: '40px' }}>
          No se encontraron productos.
        </p>
      ) : (
        <div className="grilla">
          {productosPagina.map((p) => (
            <Link
              key={p.id}
              to={`/catalogo/${p.id}`}
              className={`tarjeta ${p.stock === 0 ? 'tarjeta-agotada' : ''}`}
            >
              <div className="imagen-placeholder">[Imagen]</div>
              <span className="badge-categoria">{p.categoria}</span>
              <h3 className="producto-nombre">{p.nombre}</h3>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <p className="producto-precio">${p.precio.toLocaleString('es-CL')} CLP</p>
                {p.stock === 0 ? (
                  <span className="producto-stock-agotado">Agotado</span>
                ) : (
                  <span className="producto-stock-disponible">Disponible</span>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}

      {totalPaginas > 1 && (
        <div className="paginacion">
          <button
            onClick={() => setPagina(Math.max(1, pagina - 1))}
            disabled={pagina === 1}
            className="boton-pagina"
          >
            ‹ Anterior
          </button>
          <span className="pagina-info">
            Página {pagina} de {totalPaginas}
          </span>
          <button
            onClick={() => setPagina(Math.min(totalPaginas, pagina + 1))}
            disabled={pagina === totalPaginas}
            className="boton-pagina"
          >
            Siguiente ›
          </button>
        </div>
      )}
    </div>
  );
}

export default Catalogo;