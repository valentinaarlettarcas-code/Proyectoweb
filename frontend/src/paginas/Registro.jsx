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

    if (password !== passwordConfirm) {
      setError('Las contraseñas no coinciden.');
      return;
    }
    if (password.length < 8) {
      setError('La contraseña debe tener al menos 8 caracteres.');
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
      <div className="contenedor" style={{ maxWidth: '400px' }}>
        <h1 style={{ marginBottom: '20px' }}>Registro exitoso</h1>
        <div className="mensaje-exito">
          Te enviamos un correo a <strong>{email}</strong> para activar tu cuenta.
          <p style={{ marginTop: '6px' }}>Revisa tu bandeja de entrada (y spam) y haz clic en el enlace de activación.</p>
        </div>
        <button
          onClick={() => navigate('/login')}
          className="boton boton-secundario margin-top"
        >
          Ir a iniciar sesión
        </button>
      </div>
    );
  }

  return (
    <div className="contenedor" style={{ maxWidth: '400px' }}>
      <h1 style={{ marginBottom: '20px' }}>Crear cuenta</h1>

      {error && <div className="mensaje-error">{error}</div>}

      <form onSubmit={handleSubmit} className="formulario">
        <div className="campo">
          <label htmlFor="nombre">Nombre</label>
          <input
            type="text"
            id="nombre"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            required
          />
        </div>

        <div className="campo">
          <label htmlFor="apellido">Apellido</label>
          <input
            type="text"
            id="apellido"
            value={apellido}
            onChange={(e) => setApellido(e.target.value)}
            required
          />
        </div>

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
          <label htmlFor="password">Contraseña (mínimo 8 caracteres)</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength="8"
          />
        </div>

        <div className="campo">
          <label htmlFor="passwordConfirm">Confirmar contraseña</label>
          <input
            type="password"
            id="passwordConfirm"
            value={passwordConfirm}
            onChange={(e) => setPasswordConfirm(e.target.value)}
            required
            minLength="8"
          />
        </div>

        <button
          type="submit"
          disabled={cargando}
          className="boton boton-primario"
        >
          {cargando ? 'Procesando...' : 'Registrarme'}
        </button>
      </form>

      <p className="texto-secundario margin-top">
        ¿Ya tienes cuenta? <Link to="/login">Inicia sesión aquí</Link>
      </p>
    </div>
  );
}

export default Registro;