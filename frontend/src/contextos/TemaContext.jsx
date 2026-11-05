import { createContext, useContext, useEffect, useState } from 'react';
import { obtenerTemaActivo } from '../servicios/temas';

const TemaContext = createContext(null);

/**
 * Proveedor de tema. Carga el tema activo del backend al montar la app
 * y lo aplica como clase en el <html> para que el CSS correspondiente
 * tome el control.
 *
 * Uso:
 *   <TemaProvider>
 *     <App />
 *   </TemaProvider>
 */
export function TemaProvider({ children }) {
  const [tema, setTema] = useState(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    let cancelado = false;

    async function cargar() {
      setCargando(true);
      const t = await obtenerTemaActivo();
      if (!cancelado) {
        setTema(t);
        setCargando(false);
      }
    }

    cargar();
    return () => { cancelado = true; };
  }, []);

  // Aplicar la clase del tema en el <html>
  useEffect(() => {
    if (tema?.identificador) {
      document.documentElement.className = `tema-${tema.identificador}`;
    }
  }, [tema]);

  return (
    <TemaContext.Provider value={{ tema, cargando }}>
      {children}
    </TemaContext.Provider>
  );
}


//Hook para acceder al tema activo desde cualquier componente.

export function useTema() {
  const ctx = useContext(TemaContext);
  if (!ctx) {
    throw new Error('useTema debe usarse dentro de <TemaProvider>');
  }
  return ctx;
}