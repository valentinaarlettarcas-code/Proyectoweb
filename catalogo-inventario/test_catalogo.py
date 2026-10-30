import pytest
import requests 

BASE_URL = "http://localhost:8000/api" 

def test_paginacion_maximo_50_productos():
    # Verifica que devuelva máximo 50 productos por respuesta
    response = requests.get(f"{BASE_URL}/catalogo?page=1")
    assert response.status_code == 200
    productos = response.json().get("productos", [])
    assert len(productos) <= 50

def test_paginacion_extrema():
    # Verifica qué pasa al pedir una página que no existe
    response = requests.get(f"{BASE_URL}/catalogo?page=99999")
    assert response.status_code == 200
    productos = response.json().get("productos", [])
    assert len(productos) == 0

def test_validacion_precio_no_positivo():
    # Verifica que falle al crear un producto con precio 0
    payload = {"nombre": "Test", "precio": 0, "stock": {"disponible": 10}, "activo": True, "imagenes": ["1.jpg", "2.jpg", "3.jpg"]}
    response = requests.post(f"{BASE_URL}/productos", json=payload)
    assert response.status_code == 400 

def test_validacion_stock_negativo():
    # Verifica que falle al enviar stock negativo
    payload = {"nombre": "Test", "precio": 15000, "stock": {"disponible": -5}, "activo": True, "imagenes": ["1.jpg", "2.jpg", "3.jpg"]}
    response = requests.post(f"{BASE_URL}/productos", json=payload)
    assert response.status_code == 400

@pytest.mark.parametrize("cantidad_imagenes", [2, 4])
def test_validacion_cantidad_imagenes_estricta(cantidad_imagenes):
    # Verifica que falle si se envían 2 o 4 imágenes (exige 3 o 7)
    imagenes = [f"img_{i}.jpg" for i in range(cantidad_imagenes)]
    payload = {"nombre": "Test", "precio": 45000, "stock": {"disponible": 5}, "activo": True, "imagenes": imagenes}
    response = requests.post(f"{BASE_URL}/productos", json=payload)
    assert response.status_code == 400 

def test_productos_inactivos_no_aparecen_en_catalogo():
    # Verifica que los productos con "activo: false" 
    response = requests.get(f"{BASE_URL}/catalogo")
    productos = response.json().get("productos", [])
    inactivos = [p for p in productos if p.get("activo") is False]
    assert len(inactivos) == 0

def test_productos_agotados_no_se_pueden_agregar():
    # Verifica que un producto sin stock disponible (ejemplo: ID 18) 
    payload = {"producto_id": 18, "cantidad": 1}
    response = requests.post(f"{BASE_URL}/carrito/agregar", json=payload)
    assert response.status_code in [400, 409]