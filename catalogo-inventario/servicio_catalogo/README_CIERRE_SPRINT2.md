##  Arranque desde un clon limpio (Despliegue Local)

Sigue estos pasos para levantar el entorno del Catálogo e Inventario desde cero en tu máquina local:

### 1. Clonar y navegar:
git clone <URL_DEL_REPOSITORIO>
cd Proyectoweb-feature-catalogoinventario/catalogo-inventario/servicio_catalogo

### 2. Crear y activar el entorno virtual (Miniconda):
conda create -n catalogo_env python=3.11
conda activate catalogo_env

### 3. Instalar dependencias:
pip install -r requirements-catalogo.txt

### 4. Ejecutar el servidor:
python manage.py runserver

---

## 5. Ejecución de Tests:
Para ejecutar toda la batería de pruebas, asegúrate de estar dentro de la carpeta `servicio_catalogo` con el entorno activado y ejecuta:

python manage.py test productos
