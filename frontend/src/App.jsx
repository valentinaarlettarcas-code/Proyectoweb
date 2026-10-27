import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import Carrito from './paginas/Carrito';
import Checkout from './paginas/Checkout';
import OrdenCompra from './paginas/OrdenCompra';
import RetornoPago from './paginas/RetornoPago';
import Login from './paginas/Login';
import Registro from './paginas/Registro';
import PanelAdmin from './paginas/PanelAdmin';

function App() {
  return (
    <BrowserRouter>
      <nav style={{ padding: '10px', backgroundColor: '#333', marginBottom: '20px' }}>
        <Link to="/carrito" style={{ color: 'white', marginRight: '10px' }}>Carrito</Link>
        <Link to="/checkout" style={{ color: 'white', marginRight: '10px' }}>Checkout</Link>
        <Link to="/resumen" style={{ color: 'white' }}>Resumen</Link>
        <Link to="/login" style={{ color: 'yellow', marginLeft: '20px' }}>Login</Link>
        <Link to="/registro" style={{ color: 'yellow', marginLeft: '10px' }}>Registro</Link>
        <Link to="/admin" style={{ color: 'yellow', marginLeft: '10px' }}>Admin</Link>
      </nav>

      <Routes>
        <Route path="/" element={<Navigate to="/carrito" />} />
        <Route path="/carrito" element={<Carrito />} />
        <Route path="/checkout" element={<Checkout />} />
        <Route path="/pago/retorno" element={<RetornoPago />} />
        <Route path="/resumen" element={<OrdenCompra />} />
        <Route path="/login" element={<Login />} />
        <Route path="/registro" element={<Registro />} />
        <Route path="/admin" element={<PanelAdmin />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;