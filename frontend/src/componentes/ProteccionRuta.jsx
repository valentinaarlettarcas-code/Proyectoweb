import { Navigate } from 'react-router-dom';
import { estaAutenticado, esAdmin } from '../servicios/gestion';

/**
 * Pagina para que solo sea accesible por admins.
 * Si no hay sesion o no es admin, redirige a /login.
 */
export default function ProteccionRuta({ children }) {
  if (!estaAutenticado()) {
    return <Navigate to="/login" replace />;
  }
  if (!esAdmin()) {
    return <Navigate to="/" replace />;
  }
  return children;
}