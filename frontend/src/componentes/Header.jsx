import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { obtenerUsuarioActual, estaAutenticado, logout } from '../servicios/gestion';

function Header() {
  const navigate = useNavigate();
  const [usuario, setUsuario] = useState(obtenerUsuarioActual());
  const autenticado = estaAutenticado();

  const handleLogout = async () => {
    await logout();
    setUsuario(null);
    navigate('/login');
  };

  const estiloHeader = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '12px 20px',
    backgroundColor: 'var(--color-superficie)',
    borderBottom: '1px solid var(--color-borde)',
    position: 'sticky',
    top: 0,
    zIndex: 100,
  };

  const estiloLogo = {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    textDecoration: 'none',
  };

  const estiloNav = {
    display: 'flex',
    gap: '20px',
    alignItems: 'center',
  };

  const estiloLinkNav = {
    color: 'var(--color-texto-secundario)',
    textDecoration: 'none',
    fontSize: '15px',
  };

  const estiloAuth = {
    display: 'flex',
    gap: '12px',
    alignItems: 'center',
  };

  return (
    <header style={estiloHeader}>
      <Link to="/" style={estiloLogo}>
        <img
          src="/isotipo.png"
          alt="SETUPVERSE"
          style={{ height: '50px', width: 'auto' }}
          onError={(e) => { e.target.style.display = 'none'; }}
        />
        <span style={{ fontSize: '20px', fontWeight: 'bold', letterSpacing: '1px' }}>
          <span style={{ color: 'var(--color-texto)' }}>SETUP</span>
          <span style={{ color: 'var(--color-primario)' }}>VERSE</span>
        </span>
      </Link>

      <nav style={estiloNav}>
        <Link to="/" style={estiloLinkNav}>Inicio</Link>
        <Link to="/catalogo" style={estiloLinkNav}>Catálogo</Link>
        <Link to="/contacto" style={estiloLinkNav}>Contacto</Link>
        <Link to="/quienes-somos" style={estiloLinkNav}>Quiénes somos</Link>
        <Link to="/carrito" style={estiloLinkNav}>🛒 Carrito</Link>
      </nav>

      <div style={estiloAuth}>
        {autenticado && usuario ? (
          <>
            <span style={{ color: 'var(--color-texto-secundario)', fontSize: '14px' }}>
              Hola, {usuario.nombre || usuario.email}
            </span>
            {usuario.rol === 'ADMIN' && (
              <Link to="/admin" className="boton boton-secundario" style={{ padding: '6px 14px', fontSize: '14px' }}>
                Admin
              </Link>
            )}
            <button onClick={handleLogout} className="boton boton-error" style={{ padding: '6px 14px', fontSize: '14px' }}>
              Cerrar sesión
            </button>
          </>
        ) : (
          <>
            <Link to="/login" style={{ color: 'var(--color-primario)', fontSize: '14px' }}>
              Iniciar sesión
            </Link>
            <Link to="/registro" className="boton boton-primario" style={{ padding: '6px 14px', fontSize: '14px' }}>
              Crear cuenta
            </Link>
          </>
        )}
      </div>
    </header>
  );
}

export default Header;