import { useEffect, useState } from 'react';
import { listarTemas, obtenerTemaActivo, seleccionarTema } from '../servicios/temas';

function AdminTemas() {
  const [temas, setTemas] = useState([]);
  const [activo, setActivo] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);
  const [exito, setExito] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const [lista, act] = await Promise.all([listarTemas(), obtenerTemaActivo()]);
        setTemas(lista);
        setActivo(act);
      } catch (err) {
        setError('No se pudieron cargar los temas.');
      } finally {
        setCargando(false);
      }
    })();
  }, []);

const handleSeleccionar = async (identificador) => {
  setError(null);
  setExito(false);
  try {
    await seleccionarTema(identificador);
    setActivo({ identificador });
    setExito(true);
    // Recargar la pagina para que el TemaContext vuelva a consultar el tema activo.
    setTimeout(() => {
      window.location.reload();
    }, 1000);
  } catch (err) {
    setError('No se pudo cambiar el tema. Verifica que seas administrador.');
  }
};

  if (cargando) {
    return <div className="contenedor"><p className="texto-secundario">Cargando temas...</p></div>;
  }

  return (
    <div className="contenedor">
      <h1 style={{ marginBottom: '20px' }}>Seleccionar tema</h1>

      {error && <div className="mensaje-error">{error}</div>}
      {exito && <div className="mensaje-exito">Tema actualizado correctamente.</div>}

      <p className="texto-secundario margin-top" style={{ marginBottom: '20px' }}>
        El tema elegido se aplicará a todas las páginas públicas del sitio.
      </p>

      <div className="grilla">
        {temas.map((t) => {
          const activoId = activo?.identificador;
          const esActivo = activoId === t.identificador;
          return (
            <div key={t.identificador} className="tarjeta">
              <div className="miniatura-tema" style={estiloPreview(t.identificador)} />
              <h3 className="producto-nombre margin-top">{t.nombre}</h3>
              <p className="texto-secundario" style={{ fontSize: '13px' }}>{t.identificador}</p>
              {esActivo ? (
                <button disabled className="boton boton-secundario margin-top" style={{ width: '100%' }}>
                  ✓ Activo
                </button>
              ) : (
                <button
                  onClick={() => handleSeleccionar(t.identificador)}
                  className="boton boton-primario margin-top"
                  style={{ width: '100%' }}
                >
                  Activar
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function estiloPreview(id) {
  const previews = {
    'tema-1': { background: 'linear-gradient(135deg, #0a0a0a, #6b8cff)' },
    'tema-2': { background: 'linear-gradient(135deg, #0f0618, #c084fc)' },
    'tema-3': { background: 'linear-gradient(135deg, #f0f7ff, #0284c7)' },
    'tema-4': { background: 'linear-gradient(135deg, #faf5ff, #8b5cf6)' },
  };
  return {
    height: '80px',
    borderRadius: '6px',
    ...(previews[id] || previews['tema-1']),
  };
}

export default AdminTemas;