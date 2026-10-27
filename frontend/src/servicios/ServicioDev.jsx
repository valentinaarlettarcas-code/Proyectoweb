import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL_COMERCIO || 'http://localhost:8000/api/';

const api = axios.create({
  baseURL: API_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

function token() {
  //usamos un token de prueba
  return localStorage.getItem('token') || 'dev-test';
}

/**
 * Crea una orden de PRUEBA en backend
 * Omite Gestion y Catalogo. Crea una Order con productos ficticios.
 */
export const crearOrdenPrueba = async (checkoutId = 'dev-001') => {
  try {
    const r = await api.post('dev/crear-orden-prueba/', {
      checkout_id: checkoutId,
    }, {
      headers: { Authorization: `Token ${token()}` },
    });
    return r.data;
  } catch (error) {
    const msg = error.response?.data?.error || error.response?.data?.detail
      || error.message || 'Error al crear la orden de prueba.';
    throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
  }
};

/**
 * Crea un intento de pago en Transbank. Solo envia return_url (CC-06).
 * @param {number} idOrden - ID entero de la orden
 * @param {string} returnUrl
 */
export const iniciarPago = async (idOrden, returnUrl) => {
  try {
    const r = await api.post(`ordenes/${idOrden}/payment-attempts/`, {
      return_url: returnUrl,
    }, {
      headers: { Authorization: `Token ${token()}` },
    });
    return r.data;
  } catch (error) {
    const msg = error.response?.data?.error || error.response?.data?.detail
      || error.message || 'Error al iniciar el pago.';
    throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
  }
};