import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL_COMERCIO || 'http://localhost:8000/api/v1/';

const api = axios.create({
  baseURL: API_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

/**
 * Crea una orden pendiente en backend. El monto lo calcula el backend (CC-06).
 * @param {Array<{product_id: string, quantity: number}>} items
 */
export const crearOrden = async (items) => {
  const r = await api.post('orders/', { items });
  return r.data;
};

/**
 * Crea un intento de pago en Transbank. Solo envia return_url (CC-06).
 * @param {string} idOrden
 * @param {string} returnUrl
 */
export const iniciarPago = async (idOrden, returnUrl) => {
  try {
    const r = await api.post(`orders/${idOrden}/payment-attempts/`, {
      return_url: returnUrl,
    });
    return r.data;
  } catch (error) {
    const msg = error.response?.data?.error?.message || error.message || 'Error al iniciar el pago.';
    throw new Error(msg);
  }
};