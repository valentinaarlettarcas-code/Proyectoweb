# Guía de instalación - Proyecto Setupverse

Instrucciones para levantar todo el proyecto desde cero en un nuevo computador.

## 1. Requisitos previos

### Software a instalar

- **WSL2 con Ubuntu** (en Windows) o Ubuntu nativo
- **VS Code** con la extensión WSL
- **Git** configurado con tu correo de GitHub:
  ```bash
  git config --global user.email "tu-correo@gmail.com"
  git config --global user.name "Tu Nombre"
  ```

### Paquetes del sistema

```bash
sudo apt update
sudo apt install python3.12 python3.12-venv postgresql postgresql-contrib nodejs npm
```

## 2. Clonar el repositorio

```bash
git clone https://github.com/valentinaarlettarcas-code/Proyectoweb.git
cd Proyectoweb
git checkout feature/hu13-pago-sandbox
```

## 3. Configurar PostgreSQL (una sola vez)

```bash
# Iniciar el servicio
sudo service postgresql start

# Crear usuarios y bases de datos
sudo -u postgres createuser -s $USER
sudo -u postgres createdb comercio
sudo -u postgres createdb gestion_db
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'comercio123';"

# Configurar acceso sin password (trust)
sudo sh -c 'echo "local all all trust" > /etc/postgresql/16/main/pg_hba.conf'
sudo sh -c 'echo "host all all 127.0.0.1/32 trust" >> /etc/postgresql/16/main/pg_hba.conf'
sudo sh -c 'echo "host all all ::1/128 trust" >> /etc/postgresql/16/main/pg_hba.conf'
sudo service postgresql restart
```

## 4. Servicio de Comercio (puerto 8000)

### Instalación

```bash
cd comercio
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Variables de entorno (.env)

```
DJANGO_SECRET_KEY=cambiar-por-clave-larga-aleatoria
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_CORS_ORIGINS=http://localhost:5173

DB_NAME=comercio
DB_USER=postgres
DB_PASSWORD=comercio123
DB_HOST=localhost
DB_PORT=5432

GESTION_VERIFY_TOKEN_URL=http://127.0.0.1:8001/api/usuarios/verificar-token/
CATALOGO_API_BASE_URL=http://127.0.0.1:8002

TBK_COMMERCE_CODE=597055555532
TBK_API_KEY=579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C
TBK_ENVIRONMENT=TEST
TBK_RETURN_URL=http://localhost:5173/pago/retorno
TBK_ALLOWED_RETURN_URLS=http://localhost:5173/pago/retorno,http://127.0.0.1:5173/pago/retorno
```

### Migrar y levantar

```bash
python manage.py migrate
python manage.py runserver 8000
```

## 5. Servicio de Gestión (puerto 8001)

### Script de entorno

Gestión no usa `python-dotenv`. Crear un script para cargar las variables:

```bash
cat > ~/gestion_env.sh << 'EOF'
#!/bin/bash
export DJANGO_SECRET_KEY=cambiar-por-clave-larga-aleatoria-gestion
export DJANGO_DEBUG=True
export DB_PASSWORD=comercio123
EOF
chmod +x ~/gestion_env.sh
```

### Instalación

```bash
cd gestion
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install python-dotenv
```

### Copiar la app `temas` (no commitear)

La app `temas` está en la rama `feature/gestion-temas-contacto`. Copiarla localmente:

```bash
cd gestion
mkdir -p temas/migrations

git show origin/feature/gestion-temas-contacto:gestion/temas/__init__.py > temas/__init__.py
git show origin/feature/gestion-temas-contacto:gestion/temas/admin.py > temas/admin.py
git show origin/feature/gestion-temas-contacto:gestion/temas/apps.py > temas/apps.py
git show origin/feature/gestion-temas-contacto:gestion/temas/models.py > temas/models.py
git show origin/feature/gestion-temas-contacto:gestion/temas/serializers.py > temas/serializers.py
git show origin/feature/gestion-temas-contacto:gestion/temas/urls.py > temas/urls.py
git show origin/feature/gestion-temas-contacto:gestion/temas/views.py > temas/views.py
git show origin/feature/gestion-temas-contacto:gestion/temas/migrations/__init__.py > temas/migrations/__init__.py
git show origin/feature/gestion-temas-contacto:gestion/temas/migrations/0001_initial.py > temas/migrations/0001_initial.py
git show origin/feature/gestion-temas-contacto:gestion/temas/migrations/0002_cargar_temas_iniciales.py > temas/migrations/0002_cargar_temas_iniciales.py
git show origin/feature/gestion-temas-contacto:gestion/temas/migrations/0003_renombrar_temas.py > temas/migrations/0003_renombrar_temas.py
```

### Editar `gestion/config/settings.py`

Agregar `"temas"` a `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "usuarios",
    "temas",
]
```

### Editar `gestion/config/urls.py`

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/usuarios/', include('usuarios.urls')),
    path('api/temas/', include('temas.urls')),
]
```

### Migrar y crear superuser

```bash
source ~/gestion_env.sh
python manage.py migrate
python manage.py createsuperuser
# Email: admin@admin.com
# Password: admin (aceptar advertencia con "y")
```

### Corregir rol del superuser

```bash
python manage.py shell
```

```python
from usuarios.models import Usuario
u = Usuario.objects.get(email="admin@admin.com")
u.rol = Usuario.Rol.ADMIN
u.estado = Usuario.Estado.ACTIVO
u.is_active = True
u.is_staff = True
u.is_superuser = True
u.save()
print("Corregido.")
exit()
```

### Levantar Gestión

```bash
source ~/gestion_env.sh
python manage.py runserver 8001
```

## 6. Mock de Catálogo (puerto 8002)

Mientras el servicio real de Catálogo no está disponible, usar el mock:

### Crear el archivo `~/mock_catalogo.py`

```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import json


class MockCatalogo(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/productos/"):
            producto = {
                "nombre": "Teclado Mecánico RGB",
                "precio": "30000",
                "moneda": "CLP",
                "stock_disponible": 10,
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(producto).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8002), MockCatalogo)
    print("Mock de Catálogo corriendo en http://127.0.0.1:8002")
    server.serve_forever()
```

### Levantar el mock

```bash
python3 ~/mock_catalogo.py
```

## 7. Frontend (puerto 5173)

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### Variables de entorno (`frontend/.env`)

```
VITE_API_URL_COMERCIO=/api/comercio/
VITE_API_URL_GESTION=/api/gestion/
```

### Proxy de Vite (`frontend/vite.config.js`)

Debe tener esta configuración:

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api/gestion/usuarios': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/gestion\/usuarios/, '/api/usuarios'),
      },
      '/api/gestion': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/gestion/, '/api'),
      },
      '/api/comercio': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/comercio/, '/api'),
      },
    },
  },
})
```

## 8. Crear cliente de prueba

### Registrar desde el frontend

1. Abrir `http://localhost:5173/registro`
2. Completar: `user1@gmail.com` / `usuario1` (mínimo 8 caracteres)

### Activar manualmente (sin esperar email)

```bash
cd ~/Proyectoweb/gestion
source ~/gestion_env.sh
source .venv/bin/activate
python manage.py shell
```

```python
from usuarios.models import Usuario
u = Usuario.objects.get(email="user1@gmail.com")
u.estado = "ACTIVO"
u.is_active = True
u.save()
print("Activado.")
exit()
```

## 9. Levantar todo (4 terminales)

Necesitas 4 terminales abiertas al mismo tiempo:

### Terminal 1 - Gestión

```bash
cd ~/Proyectoweb/gestion
source ~/gestion_env.sh
source .venv/bin/activate
python manage.py runserver 8001
```

### Terminal 2 - Comercio

```bash
cd ~/Proyectoweb/comercio
source .venv/bin/activate
python manage.py runserver 8000
```

### Terminal 3 - Mock Catálogo

```bash
python3 ~/mock_catalogo.py
```

### Terminal 4 - Frontend

```bash
cd ~/Proyectoweb/frontend
npm run dev
```

## 10. Probar el flujo completo

1. Abrir `http://localhost:5173/`
2. Click en "Crear cuenta" → registrar con `user1@gmail.com` / `usuario1`
3. Activar manualmente (paso 8)
4. Click en "Iniciar sesión" → entrar con `user1@gmail.com` / `usuario1`
5. Ve a "Carrito" → click "Ir a pagar"
6. Click "Pagar con Webpay (Sandbox)"
7. Te redirige a Transbank
8. Paga con tarjeta de prueba:
   - **Tarjeta:** `4051 8856 0044 6623`
   - **CVV:** `123`
   - **Expiración:** cualquier fecha futura (ej: `12/28`)
   - **RUT:** `11.111.111-1`
9. Vuelves a `/pago/retorno` con el token_ws visible

## 11. Cambiar tema activo

Los temas se administran desde Gestión. Para cambiar el tema que ven los usuarios:
1. Iniciar como administrador
2. Editar identificador por uno de los 4 temas indicados mas abajo en el archivo `frontend/src/servicios&temas.jsx`, por ahora es prueba con un mock, pendiente integracion del endpont real.
```bash
const MOCK_TEMA = {
  identificador: 'tema-1',
  nombre: 'Azul y Morado',
};
```

Después recarga el navegador. Los temas disponibles:

| ID | Nombre | Descripción |
|---|---|---|
| `tema-1` | Medianoche | Oscuro con azul/morado |
| `tema-2` | Violeta eléctrico | Oscuro morado |
| `tema-3` | Cielo tech | Claro azul |
| `tema-4` | Lavanda | Claro lila |

## 12. Verificación rápida

Si todo está corriendo, estos endpoints deberían responder:

```bash
# Gestión responde
curl http://127.0.0.1:8001/api/temas/activo/
# Respuesta: {"identificador":"tema-1","nombre":"Medianoche"}

# Comercio responde
curl http://127.0.0.1:8000/api/ordenes/1/payment-attempts/ -X POST
# Respuesta: {"error":"Se requiere Authorization: Token <token>"} (401)

# Mock Catálogo responde
curl http://127.0.0.1:8002/api/productos/1/
# Respuesta: {"nombre":"Teclado Mecánico RGB","precio":"30000",...}

# Frontend responde
curl http://localhost:5173/
# Respuesta: HTML de la página
```

## 13. Resumen de puertos

| Servicio | Puerto | Comando |
|---|---|---|
| Gestión | 8001 | `python manage.py runserver 8001` |
| Comercio | 8000 | `python manage.py runserver 8000` |
| Mock Catálogo | 8002 | `python3 ~/mock_catalogo.py` |
| Frontend | 5173 | `npm run dev` |

## 15. Notas importantes

- Las credenciales de Transbank (`TBK_API_KEY`) son públicas de sandbox, no son secretas.
