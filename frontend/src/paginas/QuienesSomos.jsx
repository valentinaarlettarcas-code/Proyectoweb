import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { obtenerContenidoPublico } from '../servicios/contenidos';

function QuienesSomos() {
  const [contenido, setContenido] = useState(null);

  useEffect(() => {
    (async () => {
      const data = await obtenerContenidoPublico('quienes-somos');
      setContenido(data);
    })();
  }, []);

  const titulo = contenido?.titulo || 'Sobre Setupverse';
  const cuerpo = contenido?.cuerpo || 'Nacimos para que armar tu setup perfecto sea simple, accesible y sin sorpresas.';

  const valores = [
    {
      titulo: 'Calidad primero',
      descripcion: 'Seleccionamos cada producto verificando durabilidad y rendimiento. No vendemos lo que no usaríamos.',
      icono: '✓'
    },
    {
      titulo: 'Soporte real',
      descripcion: 'Respuesta en menos de 24 horas hábiles. Si algo falla, lo solucionamos sin vueltas.',
      icono: '🛟'
    },
    {
      titulo: 'Envíos en Chile',
      descripcion: 'Despachamos a todo el país con seguimiento. Santiago en 24-48 horas, regiones en 3-5 días.',
      icono: '📦'
    },
  ];

  return (
    <div className="contenedor">
      <section className="hero">
        <h1>{titulo}</h1>
        <p>{cuerpo}</p>
      </section>

      <section className="seccion">
        <h2>Nuestra historia</h2>
        <div className="tarjeta" style={{ padding: '24px', lineHeight: '1.7' }}>
          <p className="texto-secundario">
            Setupverse surge en 2026 como respuesta a una frustración común: comprar periféricos tech
            y gaming en Chile era caro, lento y con poca información. Nos propusimos cambiar eso.
          </p>
          <p className="texto-secundario" style={{ marginTop: '12px' }}>
            Empezamos como un equipo pequeño obsesionado con los detalles: teclados mecánicos, mice
            con sensor preciso, auriculares que de verdad aislan. Hoy seguimos eligiendo cada producto
            del catálogo a mano, probándolo antes de ofrecerlo.
          </p>
          <p className="texto-secundario" style={{ marginTop: '12px' }}>
            Nuestra promesa es simple: si está en la tienda, es porque nosotros lo usaríamos.
          </p>
        </div>
      </section>

      <section className="seccion">
        <h2>Nuestros valores</h2>
        <div className="grilla-categorias">
          {valores.map((v) => (
            <div key={v.titulo} className="tarjeta texto-centrado">
              <div style={{ fontSize: '40px', marginBottom: '12px' }}>{v.icono}</div>
              <h3 style={{ marginBottom: '8px' }}>{v.titulo}</h3>
              <p className="texto-secundario" style={{ fontSize: '14px' }}>{v.descripcion}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="seccion texto-centrado">
        <h2>¿Quieres saber más?</h2>
        <p className="texto-secundario" style={{ marginBottom: '20px' }}>
          Visita nuestro catálogo o contáctanos directamente.
        </p>
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link to="/catalogo" className="boton boton-primario">Ver catálogo</Link>
          <Link to="/contacto" className="boton boton-secundario">Contactarnos</Link>
        </div>
      </section>
    </div>
  );
}

export default QuienesSomos;