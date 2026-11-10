import axios from 'axios';

const api = axios.create({
  baseURL: '/api/gestion/contenidos/',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

function authHeader() {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Token ${token}` } : {};
}

/**
 * Obtiene el contenido público de una página.
 * @param {string} pagina - 'inicio', 'contacto', 'quienes-somos'
 */
export const obtenerContenidoPublico = async (pagina) => {
  try {
    const r = await api.get(`publico/${pagina}/`);
    // El backend devuelve un array; tomamos el primero.
    if (Array.isArray(r.data) && r.data.length > 0) return r.data[0];
    return r.data;
  } catch (error) {
    console.warn(`No se pudo obtener contenido de ${pagina}:`, error.message);
    return null;
  }
};

/**
 * Lista todos los contenidos (admin).
 */
export const listarContenidos = async () => {
  const r = await api.get('', { headers: authHeader() });
  return r.data;
};

/**
 * Actualiza un contenido (admin).
 */
export const actualizarContenido = async (id, datos) => {
  const r = await api.patch(`${id}/`, datos, { headers: authHeader() });
  return r.data;
};