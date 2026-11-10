import { Link } from 'react-router-dom';

function PanelAdmin() {
  const modulos = [
    { nombre: 'Usuarios', descripcion: 'Gestión de clientes y administradores', ruta: '/admin/usuarios', icono: '👥' },
    { nombre: 'Productos', descripcion: 'Crear y administrar productos del catálogo', ruta: '/admin/productos', icono: '📦' },
    { nombre: 'Contenidos', descripcion: 'Editar textos, imágenes y banners del sitio', ruta: '/admin/contenidos', icono: '📝' },
    { nombre: 'Temas', descripcion: 'Seleccionar el tema visual activo', ruta: '/admin/temas', icono: '🎨' },
    { nombre: 'Mensajes', descripcion: 'Consultar mensajes de contacto', ruta: '/admin/mensajes', icono: '✉️' },
    { nombre: 'Órdenes', descripcion: 'Consultar y administrar órdenes', ruta: '/admin/ordenes', icono: '🧾' },
  ];

  return (
    <div className="contenedor">
      <h1 style={{ marginBottom: '8px' }}>Panel administrativo</h1>
      <p className="texto-secundario" style={{ marginBottom: '30px' }}>
        Selecciona un módulo para continuar.
      </p>

      <div className="grilla-categorias">
        {modulos.map((m) => (
          m.pendiente ? (
            <div key={m.nombre} className="tarjeta" style={{ opacity: 0.5 }}>
              <div style={{ fontSize: '32px', marginBottom: '12px' }}>{m.icono}</div>
              <h3 className="producto-nombre">{m.nombre}</h3>
              <p className="texto-secundario" style={{ fontSize: '14px' }}>{m.descripcion}</p>
              <p className="texto-secundario" style={{ fontSize: '12px', marginTop: '8px' }}>(Próximamente)</p>
            </div>
          ) : (
            <Link key={m.nombre} to={m.ruta} className="tarjeta">
              <div style={{ fontSize: '32px', marginBottom: '12px' }}>{m.icono}</div>
              <h3 className="producto-nombre">{m.nombre}</h3>
              <p className="texto-secundario" style={{ fontSize: '14px' }}>{m.descripcion}</p>
            </Link>
          )
        ))}
      </div>
    </div>
  );
}

export default PanelAdmin;