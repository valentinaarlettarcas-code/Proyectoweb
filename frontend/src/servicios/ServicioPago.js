import axios from 'axios';

// cambiar para el despliege
const API_URL= import.meta.env.VITE_API_URL_COMERCIO || 'http://localhost:8000/api/comercio/';

export const iniciarPago = async (idOrden, monto) => {
    try {
        const respuesta = await axios.post('${URL_API}pagar/', {
            id_orden: idOrden,
            monto: monto,
            moneda: 'CLP'
        });
        return respuesta.data; // Retornará la URL de Transbank
    } catch (error) {
        console.error("Error al iniciar el pago:", error);
        throw error;
    }

};