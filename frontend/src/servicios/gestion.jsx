import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL_GESTION || 'http://localhost:8001/api/usuarios/';

const api = axios.create({
  baseURL: API_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

/**
 * Inicia sesion en Gestion y guarda el token en localStorage.
 * @param {string} email
 * @param {string} password
 * @returns {Promise<object>} { token, usuario: { id, nombre, apellido, email, rol, estado } }
 */
export const login = async (email, password) => {
  try {
    const r = await api.post('login/', { email, password });
    const data = r.data;
    if (data.token) {
      localStorage.setItem('token', data.token);
      localStorage.setItem('usuario', JSON.stringify(data.usuario));
    }
    return data;
  } catch (error) {
    const msg = error.response?.data?.error
      || error.response?.data?.detail
      || error.response?.data?.mensaje
      || error.message
      || 'Error al iniciar sesion.';
    throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
  }
};

/**
 * Registra un cliente nuevo. Envia email de activacion.
 * @param {object} datos { first_name, last_name, email, password }
 */
export const registro = async (datos) => {
  try {
    const r = await api.post('registro/', {
      first_name: datos.first_name,
      last_name: datos.last_name,
      email: datos.email,
      password: datos.password,
    });
    return r.data;
  } catch (error) {
    const msg = error.response?.data
      || error.response?.data?.error
      || error.message
      || 'Error al registrar el usuario.';
    throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
  }
};

// Cierra sesion

export const logout = async () => {
  const token = localStorage.getItem('token');
  if (token) {
    try {
      await api.post('logout/', {}, {
        headers: { Authorization: `Token ${token}` },
      });
    } catch (e) {
      // Si falla el logout remoto, igual limpiamos local.
      console.warn('Logout remoto fallo:', e.message);
    }
  }
  localStorage.removeItem('token');
  localStorage.removeItem('usuario');
};


//Obtiene el usuario guardado en localStorage (o null).

export const obtenerUsuarioActual = () => {
  const raw = localStorage.getItem('usuario');
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
};


//Devuelve el token guardado o null.

export const obtenerToken = () => {
  return localStorage.getItem('token');
};


//Verifica si hay sesion activa (token y usuario presentes).

export const estaAutenticado = () => {
  return Boolean(obtenerToken() && obtenerUsuarioActual());
};

//Devuelve true si el usuario actual tiene rol CLIENTE.
 export const esCliente = () => {
  const u = obtenerUsuarioActual();
  return u?.rol === 'CLIENTE';
};


//Devuelve true si el usuario actual tiene rol ADMIN.

export const esAdmin = () => {
  const u = obtenerUsuarioActual();
  return u?.rol === 'ADMIN';
};