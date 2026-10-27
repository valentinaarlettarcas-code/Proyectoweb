import {Link} from 'react-router-dom'
function Carrito(){
    return(
        <div style={{padding: '20px'}}>
            <h1> Carrito de compras</h1>
            <p>Aqui se listarán los productos del carrito.</p>
            <div style={{ marginTop: '20px', padding: '10px', border: '1px solid #ccc', width: 'fit-content' }}>
                <p><strong>Producto Simulado:</strong> Teclado Mecanico</p>
                <p>Precio: $30.000 CLP</p>
            </div>
            <Link to="/checkout">
                <button style={{ marginTop: '20px', padding: '10px 20px', cursor: 'pointer' }}>
                Ir a Pagar
                </button>
            </Link>

        </div>

    );
}
export default Carrito;