
import { useState } from "react";
import "./App.css";

const API = "/api/usuarios/";

function mensajeError(datos, codigo) {
  if (!datos || typeof datos !== "object") {
    return `Error HTTP ${codigo}`;
  }

  return Object.entries(datos)
    .map(([campo, valor]) => {
      const texto = Array.isArray(valor) ? valor.join(", ") : String(valor);
      return ["error", "detail", "non_field_errors"].includes(campo)
        ? texto
        : `${campo}: ${texto}`;
    })
    .join(" | ");
}

export default function App() {
  const [token, setToken] = useState("");
  const [admin, setAdmin] = useState(null);
  const [login, setLogin] = useState({ email: "", password: "" });
  const [usuarios, setUsuarios] = useState([]);
  const [seleccionado, setSeleccionado] = useState(null);
  const [formulario, setFormulario] = useState({
    first_name: "",
    last_name: "",
    email: "",
    rol: "CLIENTE",
  });
  const [modo, setModo] = useState("");
  const [busqueda, setBusqueda] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  async function peticion(ruta, opciones = {}, credencial = token) {
    let respuesta;

    try {
      respuesta = await fetch(API + ruta, {
        ...opciones,
        headers: {
          ...(opciones.body ? { "Content-Type": "application/json" } : {}),
          ...(credencial ? { Authorization: `Token ${credencial}` } : {}),
        },
      });
    } catch {
      throw new Error("No se puede conectar con Django. Comprueba el servidor.");
    }

    const datos = await respuesta.json().catch(() => ({}));

    if (!respuesta.ok) {
      throw new Error(mensajeError(datos, respuesta.status));
    }

    return datos;
  }

  async function cargarUsuarios(credencial = token) {
    const datos = await peticion("", {}, credencial);
    setUsuarios(Array.isArray(datos) ? datos : datos.results || []);
  }

  async function iniciarSesion(e) {
    e.preventDefault();
    setError("");
    setMensaje("");
    setCargando(true);

    try {
      const datos = await peticion("login/", {
        method: "POST",
        body: JSON.stringify(login),
      }, "");

      if (datos.usuario?.rol !== "ADMIN") {
        await peticion("logout/", { method: "POST" }, datos.token);
        throw new Error("Acceso denegado. Solo administradores.");
      }

      await cargarUsuarios(datos.token);
      setToken(datos.token);
      setAdmin(datos.usuario);
      setLogin({ email: "", password: "" });
    } catch (err) {
      setError(err.message);
    } finally {
      setCargando(false);
    }
  }

  async function cerrarSesion() {
    try {
      await peticion("logout/", { method: "POST" });
    } catch {
      // También se cierra la sesión local si falla la red.
    }
    setToken("");
    setAdmin(null);
    setUsuarios([]);
    setSeleccionado(null);
    setModo("");
    setError("");
    setMensaje("");
  }

  function nuevoUsuario() {
    setFormulario({
      first_name: "",
      last_name: "",
      email: "",
      rol: "CLIENTE",
    });
    setSeleccionado(null);
    setModo("crear");
    setError("");
    setMensaje("");
  }

  async function abrirUsuario(usuario, editar = false) {
    setError("");
    setMensaje("");

    try {
      const datos = await peticion(`${usuario.id}/`);
      setSeleccionado(datos);
      setFormulario({
        first_name: datos.first_name,
        last_name: datos.last_name,
        email: datos.email,
        rol: datos.rol,
      });
      setModo(editar ? "editar" : "detalle");
    } catch (err) {
      setError(err.message);
    }
  }

  async function guardar(e) {
    e.preventDefault();
    setCargando(true);
    setError("");
    setMensaje("");

    try {
      if (modo === "crear") {
        await peticion("admin/crear/", {
          method: "POST",
          body: JSON.stringify(formulario),
        });
        setMensaje("Usuario creado. Se ha solicitado el envío del token de activación por correo.");
      } else {
        await peticion(`${seleccionado.id}/`, {
          method: "PATCH",
          body: JSON.stringify({
            first_name: formulario.first_name,
            last_name: formulario.last_name,
            email: formulario.email,
          }),
        });
        setMensaje("Usuario actualizado correctamente.");
      }

      await cargarUsuarios();
      setModo("");
      setSeleccionado(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setCargando(false);
    }
  }

  async function cambiarEstado(usuario) {
    const bloquear = usuario.estado === "ACTIVO";
    const accion = bloquear ? "bloquear" : "desbloquear";

    if (!window.confirm(`¿Quieres ${accion} a ${usuario.email}?`)) {
      return;
    }

    setCargando(true);
    setError("");
    setMensaje("");

    try {
      await peticion(`${usuario.id}/${accion}/`, {
        method: "POST",
      });
      await cargarUsuarios();
      setModo("");
      setSeleccionado(null);
      setMensaje(`Usuario ${bloquear ? "bloqueado" : "desbloqueado"} correctamente.`);
    } catch (err) {
      setError(err.message);
    } finally {
      setCargando(false);
    }
  }

  const filtrados = usuarios.filter((u) =>
    `${u.first_name} ${u.last_name} ${u.email} ${u.rol} ${u.estado}`
      .toLowerCase()
      .includes(busqueda.toLowerCase())
  );

  if (!admin) {
    return (
      <main className="login-pagina">
        <form className="login-card" onSubmit={iniciarSesion}>
          <div className="logo">HH</div>
          <h1>Panel de Gestión</h1>
          <p>Acceso exclusivo para administradores</p>

          {error && <div className="alerta error">{error}</div>}

          <label>Correo electrónico</label>
          <input
            type="email"
            required
            value={login.email}
            onChange={(e) =>
              setLogin({ ...login, email: e.target.value })
            }
            placeholder="admin@ejemplo.com"
          />

          <label>Contraseña</label>
          <input
            type="password"
            required
            value={login.password}
            onChange={(e) =>
              setLogin({ ...login, password: e.target.value })
            }
          />

          <button className="principal" disabled={cargando}>
            {cargando ? "Entrando..." : "Iniciar sesión"}
          </button>
        </form>
      </main>
    );
  }

  return (
    <div className="aplicacion">
      <aside className="sidebar">
        <div className="marca">
          <div className="logo">HH</div>
          <strong>The HoneyHand's</strong>
        </div>

        <div className="menu-activo">◉ Gestión de usuarios</div>

        <div className="sidebar-abajo">
          <small>Administrador</small>
          <p>{admin.email}</p>
          <button onClick={cerrarSesion}>Cerrar sesión</button>
        </div>
      </aside>

      <main className="contenido">
        <header className="cabecera">
          <div>
            <span className="subtitulo">ADMINISTRACIÓN / GESTIÓN</span>
            <h1>Gestión de usuarios</h1>
            <p>Administra las cuentas registradas en la plataforma.</p>
          </div>
          <button className="principal" onClick={nuevoUsuario}>
            + Nuevo usuario
          </button>
        </header>

        {mensaje && <div className="alerta exito">{mensaje}</div>}
        {error && <div className="alerta error">{error}</div>}

        <section className="estadisticas">
          <article>
            <span>Total usuarios</span>
            <strong>{usuarios.length}</strong>
          </article>
          <article>
            <span>Activos</span>
            <strong>{usuarios.filter(u => u.estado === "ACTIVO").length}</strong>
          </article>
          <article>
            <span>Bloqueados</span>
            <strong>{usuarios.filter(u => u.estado === "BLOQUEADO").length}</strong>
          </article>
          <article>
            <span>Pendientes</span>
            <strong>{usuarios.filter(u => u.estado === "PENDIENTE").length}</strong>
          </article>
        </section>

        <section className="panel">
          <div className="panel-encabezado">
            <h2>Usuarios registrados</h2>
            <input
              placeholder="Buscar usuario..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
            />
          </div>

          <div className="tabla-scroll">
            <table>
              <thead>
                <tr>
                  <th>Usuario</th>
                  <th>Correo</th>
                  <th>Rol</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filtrados.map((u) => (
                  <tr key={u.id}>
                    <td><strong>{u.first_name} {u.last_name}</strong></td>
                    <td>{u.email}</td>
                    <td>{u.rol}</td>
                    <td>
                      <span className={`estado ${u.estado.toLowerCase()}`}>
                        {u.estado}
                      </span>
                    </td>
                    <td>
                      <div className="acciones">
                        <button onClick={() => abrirUsuario(u)}>Ver</button>
                        <button
                          disabled={u.id === admin.id}
                          onClick={() => abrirUsuario(u, true)}
                        >
                          Editar
                        </button>
                        {u.estado !== "PENDIENTE" && (
                          <button
                            disabled={cargando || u.id === admin.id}
                            onClick={() => cambiarEstado(u)}
                          >
                            {u.estado === "BLOQUEADO" ? "Desbloquear" : "Bloquear"}
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
                {filtrados.length === 0 && (
                  <tr>
                    <td colSpan="5" className="vacio">
                      No hay usuarios que coincidan.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        {modo && (
          <div className="modal-fondo">
            <section className="modal">
              <div className="modal-cabecera">
                <h2>
                  {modo === "crear" ? "Nuevo usuario" :
                   modo === "editar" ? "Editar usuario" : "Detalle del usuario"}
                </h2>
                <button onClick={() => setModo("")}>✕</button>
              </div>

              {modo === "detalle" ? (
                <div className="detalle">
                  <p><b>Nombre:</b> {seleccionado.first_name} {seleccionado.last_name}</p>
                  <p><b>Correo:</b> {seleccionado.email}</p>
                  <p><b>Rol:</b> {seleccionado.rol}</p>
                  <p><b>Estado:</b> {seleccionado.estado}</p>
                  <p><b>ID:</b> {seleccionado.id}</p>
                  <button onClick={() => setModo("")}>Cerrar</button>
                </div>
              ) : (
                <form onSubmit={guardar}>
                  <label>Nombre</label>
                  <input required value={formulario.first_name}
                    onChange={e => setFormulario({
                      ...formulario, first_name: e.target.value
                    })} />

                  <label>Apellido</label>
                  <input required value={formulario.last_name}
                    onChange={e => setFormulario({
                      ...formulario, last_name: e.target.value
                    })} />

                  <label>Correo electrónico</label>
                  <input type="email" required value={formulario.email}
                    onChange={e => setFormulario({
                      ...formulario, email: e.target.value
                    })} />

                  {modo === "crear" && (
                    <>
                      <label>Rol</label>
                      <select value={formulario.rol}
                        onChange={e => setFormulario({
                          ...formulario, rol: e.target.value
                        })}>
                        <option value="CLIENTE">Cliente</option>
                        <option value="ADMIN">Administrador</option>
                      </select>
                    </>
                  )}

                  {error && <div className="alerta error">{error}</div>}

                  <div className="botones-formulario">
                    <button type="button" onClick={() => setModo("")}>
                      Cancelar
                    </button>
                    <button className="principal" disabled={cargando}>
                      {cargando ? "Guardando..." : "Guardar"}
                    </button>
                  </div>
                </form>
              )}
            </section>
          </div>
        )}
      </main>
    </div>
  );
}
