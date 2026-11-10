import axios from 'axios';

const api = axios.create({
  baseURL: '/api/gestion/contacto/',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

/**
 * Envía un mensaje de contacto.
 * @param {object} datos - { nombre, correo, mensaje }
 * @returns {Promise<object>} respuesta del backend
 */
export const enviarMensaje = async (datos) => {
  const r = await api.post('enviar/', datos);
  return r.data;
};

//Lista los mensajes de contacto (admin).

export const listarMensajes = async () => {
  const token = localStorage.getItem('token');
  const r = await api.get('', {
    headers: token ? { Authorization: `Token ${token}` } : {},
  });
  return r.data;
};