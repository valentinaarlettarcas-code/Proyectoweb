import axios from 'axios';

// Cuando el endpoint real este en main, cambiar USE_MOCK a false.
const USE_MOCK = true;

const MOCK_TEMA = {
  identificador: 'tema-1',
  nombre: 'Azul y Morado',
};

const MOCK_TEMAS = [
  { identificador: 'azul-morado', nombre: 'Azul y Morado' },
  { identificador: 'claro-tech', nombre: 'Clasico Tech' },
  { identificador: 'oscuro-gaming', nombre: 'Oscuro Gaming' },
  { identificador: 'minimalista', nombre: 'Minimalista' },
];

/**
 * Obtiene el tema activo del backend.
 * Retorna: { identificador: string, nombre: string }
 */
export const obtenerTemaActivo = async () => {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 50));
    return MOCK_TEMA;
  }

  try {
    const r = await axios.get('/api/gestion/temas/activo/', { timeout: 5000 });
    return r.data;
  } catch (error) {
    console.warn('No se pudo obtener el tema activo, usando default:', error.message);
    return MOCK_TEMA;
  }
};


//Lista todos los temas disponibles.

export const listarTemas = async () => {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 50));
    return MOCK_TEMAS;
  }

  try {
    const r = await axios.get('/api/gestion/temas/', { timeout: 5000 });
    return r.data;
  } catch (error) {
    console.warn('No se pudo listar temas, usando default:', error.message);
    return MOCK_TEMAS;
  }
};