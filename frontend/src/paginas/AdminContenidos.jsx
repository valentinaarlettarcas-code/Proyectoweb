import { useEffect, useState } from 'react';
import { listarContenidos, actualizarContenido } from '../servicios/contenidos';

function AdminContenidos() {
  const [items, setItems] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [editando, setEditando] = useState(null);
  const [form, setForm] = useState({});
  const [error, setError] = useState(null);
  const [exito, setExito] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const data = await listarContenidos();
        setItems(data);
      } catch (err) {
        setError('No se pudieron cargar los contenidos.');
      } finally {
        setCargando(false);
      }
    })();
  }, []);

  const handleEditar = (item) => {
    setEditando(item.id);
    setForm({ titulo: item.titulo || '', cuerpo: item.cuerpo || '' });
    setExito(false);
    setError(null);
  };

  const handleCancelar = () => {
    setEditando(null);
    setForm({});
  };

  const handleGuardar = async (id) => {
    setError(null);
    setExito(false);
    try {
      const actualizado = await actualizarContenido(id, form);
      setItems(items.map((it) => (it.id === id ? actualizado : it)));
      setExito(true);
      setEditando(null);
    } catch (err) {
      setError('No se pudo guardar. Verifica tu sesión de admin.');
    }
  };

  if (cargando) {
    return <div className="contenedor"><p className="texto-secundario">Cargando contenidos...</p></div>;
  }

  return (
    <div className="contenedor">
      <h1 style={{ marginBottom: '20px' }}>Editar contenidos</h1>

      {error && <div className="mensaje-error">{error}</div>}
      {exito && <div className="mensaje-exito">Contenido actualizado correctamente.</div>}

      {items.length === 0 ? (
        <p className="texto-secundario">No hay contenidos para editar.</p>
      ) : (
        <div className="grilla">
          {items.map((item) => (
            <div key={item.id} className="tarjeta">
              <h3 className="producto-nombre">{item.pagina} / {item.clave}</h3>
              {editando === item.id ? (
                <div className="formulario margin-top">
                  <div className="campo">
                    <label htmlFor={`titulo-${item.id}`}>Título</label>
                    <input
                      type="text"
                      id={`titulo-${item.id}`}
                      value={form.titulo}
                      onChange={(e) => setForm({ ...form, titulo: e.target.value })}
                    />
                  </div>
                  <div className="campo">
                    <label htmlFor={`cuerpo-${item.id}`}>Cuerpo</label>
                    <textarea
                      id={`cuerpo-${item.id}`}
                      value={form.cuerpo}
                      onChange={(e) => setForm({ ...form, cuerpo: e.target.value })}
                    />
                  </div>
                  <div style={{ display: 'flex', gap: '8px', marginTop: '10px' }}>
                    <button onClick={() => handleGuardar(item.id)} className="boton boton-primario">Guardar</button>
                    <button onClick={handleCancelar} className="boton boton-secundario">Cancelar</button>
                  </div>
                </div>
              ) : (
                <>
                  <p className="texto-secundario" style={{ fontSize: '14px', margin: '6px 0' }}>
                    <strong>Título:</strong> {item.titulo || '(vacío)'}
                  </p>
                  <p className="texto-secundario" style={{ fontSize: '14px', margin: '6px 0' }}>
                    <strong>Cuerpo:</strong> {item.cuerpo || '(vacío)'}
                  </p>
                  <button onClick={() => handleEditar(item)} className="boton boton-secundario margin-top">
                    Editar
                  </button>
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AdminContenidos;