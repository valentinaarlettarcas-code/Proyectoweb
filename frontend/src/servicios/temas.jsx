import axios from 'axios';

const api = axios.create({
  baseURL: '/api/gestion/temas/',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

function authHeader() {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Token ${token}` } : {};
}


/**
 * Obtiene el tema activo del backend.
 * Retorna: { identificador: string, nombre: string }
 */
export const obtenerTemaActivo = async () => {

  try {
    const r = await api.get('activo/', { timeout: 5000 });
    return r.data;
  } catch (error) {
    console.warn('No se pudo obtener el tema activo, usando default:', error.message);
    return {identificador: 'tema-1', nombre: 'Medianoche'};
  }
};


//Lista todos los temas disponibles.

export const listarTemas = async () => {
  try {
    const r = await api.get('.');
    const data = r.data;
    if (Array.isArray(data)) return data;
    if (data && Array.isArray(data.results)) return data.results;
    return [];
  } catch (error) {
    console.warn('No se pudieron listar temas:', error.message);
    return [];
  }
};

/**
 * Selecciona el tema activo (admin).
 * @param {string} identificador - 'tema-1', 'tema-2', etc.
 */
export const seleccionarTema = async (identificador) => {
  const r = await api.post('seleccionar/', { tema: identificador }, { headers: authHeader() });
  return r.data;
};