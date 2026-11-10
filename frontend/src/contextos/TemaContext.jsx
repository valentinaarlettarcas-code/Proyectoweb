import { createContext, useContext, useEffect, useState } from 'react';
import { obtenerTemaActivo } from '../servicios/temas';

const TemaContext = createContext(null);

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
      console.log('Tema aplicado:', tema.identificador);
    }
  }, [tema]);

  return (
    <TemaContext.Provider value={{ tema, cargando }}>
      {children}
    </TemaContext.Provider>
  );
}

export function useTema() {
  const ctx = useContext(TemaContext);
  if (!ctx) {
    throw new Error('useTema debe usarse dentro de <TemaProvider>');
  }
  return ctx;
}