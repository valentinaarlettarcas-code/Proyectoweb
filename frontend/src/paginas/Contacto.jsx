
function Contacto() {
  return (
    <div>
      <h1>Contacto</h1>

      <p>¿Tienes alguna consulta? ¡Contáctanos!</p>

      <p>Correo: contacto@setupverse.cl</p>
      <p>Teléfono: +56 9 1234 5678</p>

      <form>
        <label>Nombre:</label>
        <input type="text" placeholder="Tu nombre" />

        <br />

        <label>Correo:</label>
        <input type="email" placeholder="Tu correo" />

        <br />

        <label>Mensaje:</label>
        <textarea placeholder="Escribe tu mensaje" />

        <br />

        <button type="submit">Enviar</button>
      </form>
    </div>
  );
}

export default Contacto;
