import os
import requests
from rest_framework import exceptions

def verificar_token_cliente(request):
    """
    Verifica el token contra el microservicio de Gestión.
    Exige rol CLIENTE y estado ACTIVO, usando timeout y variable de entorno.
    Retorna el usuario.id si todo está correctamente válidado. 
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise exceptions.AuthenticationFailed('Token de autenticación no proporcionado.')

    # Toma la URL de la variable de entorno o usa un valor por defecto seguro
    url = os.environ.get('GESTION_VERIFY_TOKEN_URL', 'http://localhost:8000/api/verificar-token/')
    
    try:
        # Usa un timeout de 5 segundos para no colgar el servicio Comercio si Gestión falla
        response = requests.get(url, headers={'Authorization': auth_header}, timeout=5.0)
    except requests.exceptions.Timeout:
        raise exceptions.APIException('Timeout: El servicio de Gestión tardó demasiado en responder.')
    except requests.exceptions.RequestException:
        raise exceptions.APIException('Error de conexión con el servicio de Gestión.')

    if response.status_code != 200:
        raise exceptions.AuthenticationFailed('Token inválido o expirado!!')

    data = response.json()
    
    usuario_id = data.get('id')
    rol = data.get('rol')
    estado = data.get('estado')

    # Validaciones exigidas por el enunciado y el equipo
    if not usuario_id:
        raise exceptions.AuthenticationFailed('El servicio de Gestión no devolvió el usuario.id!.')
    if rol != 'CLIENTE':
        raise exceptions.PermissionDenied('Acceso denegado!!Se requiere rol de CLIENTE para esta operación.')
    if estado != 'ACTIVO':
        raise exceptions.PermissionDenied('Acceso denegado!!La cuenta del usuario no está ACTIVO.')

    return usuario_id