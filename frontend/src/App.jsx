import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import { TemaProvider } from './contextos/TemaContext';
import Header from './componentes/Header';
import Inicio from './paginas/Inicio';
import Catalogo from './paginas/Catalogo';
import DetalleProducto from './paginas/DetalleProducto';
import Carrito from './paginas/Carrito';
import Checkout from './paginas/Checkout';
import OrdenCompra from './paginas/OrdenCompra';
import RetornoPago from './paginas/RetornoPago';
import Login from './paginas/Login';
import Registro from './paginas/Registro';
import PanelAdmin from './paginas/PanelAdmin';
import Contacto from './paginas/Contacto';
import QuienesSomos from './paginas/QuienesSomos';

function App() {
  return (
    <TemaProvider>
      <BrowserRouter>
        <Header />
        <Routes>
          <Route path="/" element={<Inicio />} />
          <Route path="/catalogo" element={<Catalogo />} />
          <Route path="/catalogo/:id" element={<DetalleProducto />} />
          <Route path="/carrito" element={<Carrito />} />
          <Route path="/checkout" element={<Checkout />} />
          <Route path="/pago/retorno" element={<RetornoPago />} />
          <Route path="/resumen" element={<OrdenCompra />} />
          <Route path="/login" element={<Login />} />
          <Route path="/registro" element={<Registro />} />
          <Route path="/admin" element={<PanelAdmin />} />
          <Route path="/contacto" element={<Contacto />} />
          <Route path="/quienes-somos" element={<QuienesSomos />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    </TemaProvider>
  );
}

export default App;