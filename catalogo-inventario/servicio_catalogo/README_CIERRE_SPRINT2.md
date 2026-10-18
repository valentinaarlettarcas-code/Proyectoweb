### Manual de Arranque (Desde un clon limpio)

> ** IMPORTANTE PARA USUARIOS DE WINDOWS:**
> Para evitar errores con la creación del entorno virtual, **NO** uses la terminal integrada de Visual Studio Code (PowerShell). Debes realizar todos los pasos de consola abriendo la aplicación **Anaconda Prompt** (o Miniconda Prompt) desde el menú de Inicio de Windows.

Abre tu terminal y ejecuta el siguiente bloque de comandos. Cada paso está comentado para explicar su función:

```bash
# 1. Clonar el repositorio
git clone [https://github.com/valentinaarlettarcas-code/Proyectoweb.git](https://github.com/valentinaarlettarcas-code/Proyectoweb.git)
cd Proyectoweb

# 2. Actualizar referencias y cambiar a la rama de la feature
git fetch
git checkout feature/catalogoinventario-diseño

# 3. Entrar a la carpeta específica del microservicio
cd catalogo-inventario\servicio_catalogo

# 4. Crear el entorno virtual con Python 3.12 y activarlo
conda create -n catalogo_env python=3.12 -y
conda activate catalogo_env

# 5. Instalar las dependencias (Django, MongoDB, etc.)
pip install -r requirements-catalogo.txt

# 6. Configurar variables de entorno (Credenciales y Seguridad obligatorias)
set DJANGO_SECRET_KEY=clave_temporal_de_prueba_12345
set CATALOGO_MONGO_URI=mongodb+srv://<usuario>:<password>@cluster.mongodb.net/catalogo_db
set CATALOGO_INTERNAL_TOKEN=token_interno_dev_123
set CATALOGO_ADMIN_TOKEN=token_admin_dev_123

# 7. Ejecutar las pruebas automatizadas (la consola debe devolver "OK")
python manage.py test productos

# 8. Levantar el servidor en el puerto 8001 (definido en el contrato API)
python manage.py runserver 8001