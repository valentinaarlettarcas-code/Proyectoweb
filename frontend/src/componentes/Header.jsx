import { Link, useNavigate } from 'react-router-dom';
import { obtenerUsuarioActual, estaAutenticado, logout } from '../servicios/gestion';
import { useState } from 'react';

function Header() {
  const navigate = useNavigate();
  const [usuario, setUsuario] = useState(obtenerUsuarioActual());
  const autenticado = estaAutenticado();

  const handleLogout = async () => {
    await logout();
    setUsuario(null);
    navigate('/login');
  };

  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '12px 20px',
      backgroundColor: '#0a0a0a',
      borderBottom: '1px solid #1f1f1f',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      {/* Logo */}
      <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '10px', textDecoration: 'none' }}>
        <img
          src="/logo.png"
          alt="SETUPVERSE"
          style={{ height: '40px', width: 'auto' }}
          onError={(e) => { e.target.style.display = 'none'; }}
        />
        <span style={{
          color: 'white',
          fontSize: '20px',
          fontWeight: 'bold',
          letterSpacing: '1px',
        }}>
          <span style={{ color: 'white' }}>SETUP</span>
          <span style={{ color: '#6b8cff' }}>VERSE</span>
        </span>
      </Link>

      {/* Nav principal */}
      <nav style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
        <Link to="/" style={navLinkStyle}>Inicio</Link>
        <Link to="/catalogo" style={navLinkStyle}>Catálogo</Link>
        <Link to="/contacto" style={navLinkStyle}>Contacto</Link>
        <Link to="/quienes-somos" style={navLinkStyle}>Quiénes somos</Link>
        <Link to="/carrito" style={navLinkStyle}>🛒 Carrito</Link>
      </nav>

      {/* Usuario / auth */}
      <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
        {autenticado && usuario ? (
          <>
            <span style={{ color: '#aaa', fontSize: '14px' }}>
              Hola, {usuario.nombre || usuario.email}
            </span>
            {usuario.rol === 'ADMIN' && (
              <Link to="/admin" style={authLinkStyle}>Admin</Link>
            )}
            <button onClick={handleLogout} style={logoutButtonStyle}>
              Cerrar sesión
            </button>
          </>
        ) : (
          <>
            <Link to="/login" style={authLinkStyle}>Iniciar sesión</Link>
            <Link to="/registro" style={registerButtonStyle}>Crear cuenta</Link>
          </>
        )}
      </div>
    </header>
  );
}

const navLinkStyle = {
  color: '#ccc',
  textDecoration: 'none',
  fontSize: '15px',
  transition: 'color 0.2s',
};

const authLinkStyle = {
  color: '#6b8cff',
  textDecoration: 'none',
  fontSize: '14px',
};

const registerButtonStyle = {
  color: 'white',
  backgroundColor: '#6b8cff',
  padding: '6px 14px',
  borderRadius: '4px',
  textDecoration: 'none',
  fontSize: '14px',
};

const logoutButtonStyle = {
  color: '#ff6b6b',
  backgroundColor: 'transparent',
  border: '1px solid #ff6b6b',
  padding: '5px 12px',
  borderRadius: '4px',
  cursor: 'pointer',
  fontSize: '13px',
};

export default Header;