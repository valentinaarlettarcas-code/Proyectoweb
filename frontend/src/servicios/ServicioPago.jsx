import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL_COMERCIO || '/api/comercio/';

const api = axios.create({
  baseURL: API_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

function token() {
  return localStorage.getItem('token') || '';
}

/**
 * Crea una orden en backend. El monto lo calcula el backend (CC-06).
 * @param {Array<{producto_id: number, quantity: number}>} items
 * @param {string} checkoutId
 */
export const crearOrden = async (items, checkoutId) => {
  try {
    const r = await api.post('ordenes/', {
      checkout_id: checkoutId,
      items,
    }, {
      headers: { Authorization: `Token ${token()}` },
    });
    return r.data;
  } catch (error) {
    const msg = error.response?.data?.error || error.response?.data?.detail
      || error.message || 'Error al crear la orden.';
    throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
  }
};

/**
 * Crea un intento de pago en Transbank. Solo envia return_url (CC-06).
 * @param {number} idOrden
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