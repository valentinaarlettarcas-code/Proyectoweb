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
      // Redirigir segun rol
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
    <div style={{ padding: '20px', maxWidth: '400px', margin: '0 auto' }}>
      <h1>Iniciar sesion</h1>

      {error && (
        <div style={{ padding: '10px', backgroundColor: '#fee', border: '1px solid #c33', margin: '10px 0' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <label>
          Correo:
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', marginTop: '4px' }}
          />
        </label>

        <label>
          Contraseña:
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', marginTop: '4px' }}
          />
        </label>

        <button
          type="submit"
          disabled={cargando}
          style={{
            padding: '10px',
            marginTop: '10px',
            cursor: cargando ? 'not-allowed' : 'pointer',
            opacity: cargando ? 0.6 : 1,
          }}
        >
          {cargando ? 'Procesando...' : 'Iniciar sesion'}
        </button>
      </form>

      <p style={{ marginTop: '15px' }}>
        ¿No tienes cuenta? <Link to="/registro">Registrate aqui</Link>
      </p>
    </div>
  );
}

export default Login;