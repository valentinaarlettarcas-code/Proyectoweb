import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { TemaProvider } from './contextos/TemaContext';
import Header from './componentes/Header';
import ProteccionRuta from './componentes/ProteccionRuta';
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
import AdminContenidos from './paginas/AdminContenidos';
import AdminTemas from './paginas/AdminTemas';
import Contacto from './paginas/Contacto';
import QuienesSomos from './paginas/QuienesSomos';

function App() {
  return (
    <TemaProvider>
      <BrowserRouter>
        <a href="#contenido-principal" className="saltar-contenido">Saltar al contenido principal</a>
        <Header />
        <main id="contenido-principal">
        <Routes>
          {/* Páginas públicas */}
          <Route path="/" element={<Inicio />} />
          <Route path="/catalogo" element={<Catalogo />} />
          <Route path="/catalogo/:id" element={<DetalleProducto />} />
          <Route path="/contacto" element={<Contacto />} />
          <Route path="/quienes-somos" element={<QuienesSomos />} />
          <Route path="/carrito" element={<Carrito />} />
          <Route path="/pago/retorno" element={<RetornoPago />} />
          <Route path="/login" element={<Login />} />
          <Route path="/registro" element={<Registro />} />

          {/* Cliente autenticado */}
          <Route path="/checkout" element={<Checkout />} />
          <Route path="/resumen" element={<OrdenCompra />} />

          {/* Admin (protegidas) */}
          <Route path="/admin" element={<ProteccionRuta><PanelAdmin /></ProteccionRuta>} />
          <Route path="/admin/contenidos" element={<ProteccionRuta><AdminContenidos /></ProteccionRuta>} />
          <Route path="/admin/temas" element={<ProteccionRuta><AdminTemas /></ProteccionRuta>} />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
        </main>
      </BrowserRouter>
    </TemaProvider>
  );
}

export default App;