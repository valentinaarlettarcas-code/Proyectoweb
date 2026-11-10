import { useEffect, useState } from 'react';
import { enviarMensaje } from '../servicios/contactos';
import { obtenerContenidoPublico } from '../servicios/contenidos';

function Contacto() {
  const [contenido, setContenido] = useState(null);
  const [form, setForm] = useState({ nombre: '', correo: '', mensaje: '' });
  const [errores, setErrores] = useState({});
  const [enviando, setEnviando] = useState(false);
  const [exito, setExito] = useState(false);

  useEffect(() => {
    (async () => {
      const data = await obtenerContenidoPublico('contacto');
      setContenido(data);
    })();
  }, []);

  const titulo = contenido?.titulo || 'Contacto';
  const cuerpo = contenido?.cuerpo || '¿Tienes preguntas? Escríbenos y te responderemos a la brevedad.';

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (enviando) return;
    setErrores({});
    setEnviando(true);

    try {
      await enviarMensaje(form);
      setExito(true);
      setForm({ nombre: '', correo: '', mensaje: '' });
    } catch (err) {
      const data = err.response?.data;
      if (data && typeof data === 'object') {
        setErrores(data);
      } else {
        setErrores({ general: err.message || 'No se pudo enviar el mensaje.' });
      }
    } finally {
      setEnviando(false);
    }
  };

  if (exito) {
    return (
      <div className="contenedor" style={{ maxWidth: '600px' }}>
        <h1>Mensaje enviado</h1>
        <div className="mensaje-exito">
          Recibimos tu mensaje. Te responderemos a la brevedad.
        </div>
        <button
          onClick={() => setExito(false)}
          className="boton boton-secundario margin-top"
        >
          Enviar otro mensaje
        </button>
      </div>
    );
  }

  return (
    <div className="contenedor" style={{ maxWidth: '600px' }}>
      <h1 style={{ marginBottom: '20px' }}>{titulo}</h1>
      <p className="texto-secundario" style={{ marginBottom: '20px' }}>{cuerpo}</p>

      {errores.general && <div className="mensaje-error">{errores.general}</div>}

      <form onSubmit={handleSubmit} className="formulario">
        <div className="campo">
          <label htmlFor="nombre">Nombre</label>
          <input
            type="text"
            id="nombre"
            name="nombre"
            value={form.nombre}
            onChange={handleChange}
            required
            minLength="2"
            maxLength="100"
          />
          {errores.nombre && (
            <span className="producto-stock-agotado" style={{ fontSize: '13px' }}>
              {errores.nombre}
            </span>
          )}
        </div>

        <div className="campo">
          <label htmlFor="correo">Correo</label>
          <input
            type="email"
            id="correo"
            name="correo"
            value={form.correo}
            onChange={handleChange}
            required
          />
          {errores.correo && (
            <span className="producto-stock-agotado" style={{ fontSize: '13px' }}>
              {errores.correo}
            </span>
          )}
        </div>

        <div className="campo">
          <label htmlFor="mensaje">Mensaje</label>
          <textarea
            id="mensaje"
            name="mensaje"
            value={form.mensaje}
            onChange={handleChange}
            required
            minLength="10"
            maxLength="2000"
          />
          {errores.mensaje && (
            <span className="producto-stock-agotado" style={{ fontSize: '13px' }}>
              {errores.mensaje}
            </span>
          )}
        </div>

        <button
          type="submit"
          disabled={enviando}
          className="boton boton-primario"
        >
          {enviando ? 'Enviando...' : 'Enviar mensaje'}
        </button>
      </form>

      <div className="seccion margin-top-grande">
        <h2>Información de contacto</h2>
        <div className="tarjeta" style={{ padding: '20px' }}>
          <p style={{ marginBottom: '8px' }}><strong>Email:</strong> soporte@setupverse.cl</p>
          <p style={{ marginBottom: '8px' }}><strong>Teléfono:</strong> +56 2 2345 6789</p>
          <p style={{ marginBottom: '8px' }}><strong>Horario:</strong> Lunes a Viernes, 9:00 - 18:00</p>
          <p><strong>Dirección:</strong> Av. Providencia 1234, Santiago, Chile</p>
        </div>
      </div>
    </div>
  );
}

export default Contacto;