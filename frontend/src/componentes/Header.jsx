import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { obtenerUsuarioActual, estaAutenticado, logout } from '../servicios/gestion';

function Header() {
  const navigate = useNavigate();
  const [usuario, setUsuario] = useState(obtenerUsuarioActual());
  const autenticado = estaAutenticado();
  const [menuAbierto, setMenuAbierto] = useState(false);

  const handleLogout = async () => {
    await logout();
    setUsuario(null);
    navigate('/login');
  };

  const toggleMenu = () => setMenuAbierto(!menuAbierto);
  const cerrarMenu = () => setMenuAbierto(false);

  return (
    <header className="header">
      <Link to="/" className="header-logo" onClick={cerrarMenu} aria-label="Inicio Setupverse">
        <img
          src="/isotipo.png"
          alt="Logo de Setupverse"
          style={{ height: '50px', width: 'auto' }}
          onError={(e) => { e.target.style.display = 'none'; }}
        />
        <span style={{ fontSize: '20px', fontWeight: 'bold', letterSpacing: '1px' }}>
          <span style={{ color: 'var(--color-texto)' }}>SETUP</span>
          <span style={{ color: 'var(--color-primario)' }}>VERSE</span>
        </span>
      </Link>

      <button
        onClick={toggleMenu}
        className="header-boton-menu"
        aria-label={menuAbierto ? "Cerrar menú" : "Abrir menú"}
        aria-expanded={menuAbierto}
      >
        ☰ Menú
      </button>

      <nav className={`header-nav ${menuAbierto ? 'abierto' : ''}`} aria-label="Navegación principal">
        <Link to="/" className="header-link-nav" onClick={cerrarMenu}>Inicio</Link>
        <Link to="/catalogo" className="header-link-nav" onClick={cerrarMenu}>Catálogo</Link>
        <Link to="/contacto" className="header-link-nav" onClick={cerrarMenu}>Contacto</Link>
        <Link to="/quienes-somos" className="header-link-nav" onClick={cerrarMenu}>Quiénes somos</Link>
        <Link to="/carrito" className="header-link-nav" onClick={cerrarMenu}>🛒 Carrito</Link>

        <div className="header-auth">
          {autenticado && usuario ? (
            <>
              <span className="header-usuario" aria-label={`Hola ${usuario.nombre || usuario.email}`}>
                Hola, {usuario.nombre || usuario.email}
              </span>
              {usuario.rol === 'ADMIN' && (
                <Link to="/admin" className="boton boton-secundario" style={{ padding: '6px 14px', fontSize: '14px' }} onClick={cerrarMenu}>
                  Admin
                </Link>
              )}
              <button onClick={handleLogout} className="boton boton-error" style={{ padding: '6px 14px', fontSize: '14px' }} aria-label="Cerrar sesión">
                Cerrar sesión
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="header-link-nav" style={{ color: 'var(--color-primario)' }} onClick={cerrarMenu}>
                Iniciar sesión
              </Link>
              <Link to="/registro" className="boton boton-primario" style={{ padding: '6px 14px', fontSize: '14px' }} onClick={cerrarMenu}>
                Crear cuenta
              </Link>
            </>
          )}
        </div>
      </nav>
    </header>
  );
}

export default Header;