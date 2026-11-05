import { useState } from 'react';

function Contacto() {
  const [form, setForm] = useState({ nombre: '', email: '', mensaje: '' });
  const [errores, setErrores] = useState({});
  const [enviando, setEnviando] = useState(false);
  const [exito, setExito] = useState(false);

  const validar = () => {
    const e = {};
    if (!form.nombre || form.nombre.trim().length < 2) {
      e.nombre = 'El nombre debe tener al menos 2 caracteres.';
    } else if (form.nombre.trim().length > 100) {
      e.nombre = 'El nombre no puede superar 100 caracteres.';
    }
    if (!form.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      e.email = 'Ingresa un correo válido.';
    }
    if (!form.mensaje || form.mensaje.trim().length < 10) {
      e.mensaje = 'El mensaje debe tener al menos 10 caracteres.';
    } else if (form.mensaje.trim().length > 2000) {
      e.mensaje = 'El mensaje no puede superar 2000 caracteres.';
    }
    setErrores(e);
    return Object.keys(e).length === 0;
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (enviando) return;
    if (!validar()) return;

    setEnviando(true);
    try {
      // PENDIENTE llamar al backend /api/contacto/ cuando este disponible
      await new Promise((r) => setTimeout(r, 500));
      setExito(true);
      setForm({ nombre: '', email: '', mensaje: '' });
      setEnviando(false);
    } catch (err) {
      setErrores({ mensaje: 'No se pudo enviar el mensaje. Intenta nuevamente.' });
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
          className="boton boton-secundario"
          style={{ marginTop: '15px' }}
        >
          Enviar otro mensaje
        </button>
      </div>
    );
  }

  return (
    <div className="contenedor" style={{ maxWidth: '600px' }}>
      <h1>Contacto</h1>
      <p className="texto-secundario" style={{ marginBottom: '20px' }}>
        ¿Tienes preguntas? Escríbenos y te responderemos a la brevedad.
      </p>

      <form onSubmit={handleSubmit} className="formulario">
        <div className="campo">
          <label htmlFor="nombre">Nombre</label>
          <input
            type="text"
            id="nombre"
            name="nombre"
            value={form.nombre}
            onChange={handleChange}
            maxLength={100}
          />
          {errores.nombre && <span className="producto-stock-agotado" style={{ fontSize: '13px' }}>{errores.nombre}</span>}
        </div>

        <div className="campo">
          <label htmlFor="email">Correo</label>
          <input
            type="email"
            id="email"
            name="email"
            value={form.email}
            onChange={handleChange}
          />
          {errores.email && <span className="producto-stock-agotado" style={{ fontSize: '13px' }}>{errores.email}</span>}
        </div>

        <div className="campo">
          <label htmlFor="mensaje">Mensaje</label>
          <textarea
            id="mensaje"
            name="mensaje"
            value={form.mensaje}
            onChange={handleChange}
            maxLength={2000}
          />
          {errores.mensaje && <span className="producto-stock-agotado" style={{ fontSize: '13px' }}>{errores.mensaje}</span>}
          <span className="texto-secundario" style={{ fontSize: '12px' }}>
            {form.mensaje.length}/2000 caracteres
          </span>
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
          <p style={{ marginBottom: '8px' }}><strong>Teléfono:</strong> +56 9 1234 5679</p>
          <p style={{ marginBottom: '8px' }}><strong>Horario:</strong> Lunes a Viernes, 9:00 - 18:00</p>
          <p><strong>Dirección:</strong> Av. Providencia 1234, Santiago, Chile</p>
        </div>
      </div>
    </div>
  );
}

export default Contacto;