import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { login } from '../servicios/gestion';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (cargando) return;
    setCargando(true);
    setError(null);
    try {
      const data = await login(email, password);
      if (data.usuario.rol === 'ADMIN') {
        navigate('/admin');
      } else {
        const redirect = new URLSearchParams(window.location.search).get('redirect');
        navigate(redirect || '/carrito');
      }
    } catch (err) {
      setError(err.message);
      setCargando(false);
    }
  };

  return (
    <div className="contenedor" style={{ maxWidth: '400px' }}>
      <h1 style={{ marginBottom: '20px' }}>Iniciar sesión</h1>

      {error && <div className="mensaje-error">{error}</div>}

      <form onSubmit={handleSubmit} className="formulario">
        <div className="campo">
          <label htmlFor="email">Correo</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div className="campo">
          <label htmlFor="password">Contraseña</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <button
          type="submit"
          disabled={cargando}
          className="boton boton-primario"
        >
          {cargando ? 'Procesando...' : 'Iniciar sesión'}
        </button>
      </form>

      <p className="texto-secundario margin-top">
        ¿No tienes cuenta? <Link to="/registro">Regístrate aquí</Link>
      </p>
    </div>
  );
}

export default Login;