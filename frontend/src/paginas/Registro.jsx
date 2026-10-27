import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { registro } from '../servicios/gestion';

function Registro() {
  const [nombre, setNombre] = useState('');
  const [apellido, setApellido] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);
  const [exito, setExito] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (cargando) return;

    // Validacion local de coincidencia de passwords
    if (password !== passwordConfirm) {
      setError('Las contrasenas no coinciden.');
      return;
    }
    if (password.length < 8) {
      setError('La contrasena debe tener al menos 8 caracteres.');
      return;
    }

    setCargando(true);
    setError(null);
    try {
      await registro({
        first_name: nombre,
        last_name: apellido,
        email,
        password,
      });
      setExito(true);
      setCargando(false);
    } catch (err) {
      setError(err.message);
      setCargando(false);
    }
  };

  if (exito) {
    return (
      <div style={{ padding: '20px', maxWidth: '400px', margin: '0 auto' }}>
        <h1>Registro exitoso</h1>
        <div style={{ padding: '15px', backgroundColor: '#efe', border: '1px solid #3c3', margin: '10px 0' }}>
          <p>Te enviamos un correo a <strong>{email}</strong> para activar tu cuenta.</p>
          <p>Revisa tu bandeja de entrada (y spam) y haz clic en el enlace de activacion.</p>
        </div>
        <button
          onClick={() => navigate('/login')}
          style={{ padding: '10px 20px', cursor: 'pointer' }}
        >
          Ir a iniciar sesion
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', maxWidth: '400px', margin: '0 auto' }}>
      <h1>Crear cuenta</h1>

      {error && (
        <div style={{ padding: '10px', backgroundColor: '#fee', border: '1px solid #c33', margin: '10px 0' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <label>
          Nombre:
          <input
            type="text"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', marginTop: '4px' }}
          />
        </label>

        <label>
          Apellido:
          <input
            type="text"
            value={apellido}
            onChange={(e) => setApellido(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', marginTop: '4px' }}
          />
        </label>

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
          Contrasena (minimo 8 caracteres):
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength="8"
            style={{ width: '100%', padding: '8px', marginTop: '4px' }}
          />
        </label>

        <label>
          Confirmar contrasena:
          <input
            type="password"
            value={passwordConfirm}
            onChange={(e) => setPasswordConfirm(e.target.value)}
            required
            minLength="8"
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
          {cargando ? 'Procesando...' : 'Registrarme'}
        </button>
      </form>

      <p style={{ marginTop: '15px' }}>
        ¿Ya tienes cuenta? <Link to="/login">Inicia sesion aqui</Link>
      </p>
    </div>
  );
}

export default Registro;