import os
import requests
from rest_framework import exceptions, status

# Excepción para forzar el código cuando Gestión falla
class ServiceUnavailable(exceptions.APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Servicio de Gestión temporalmente no disponible.'
    default_code = 'service_unavailable'

def verificar_token_cliente(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise exceptions.AuthenticationFailed('Token de autenticación no proporcionado.')

    # URL exacta de Gestión
    url = os.environ.get('GESTION_VERIFY_TOKEN_URL', 'http://localhost:8000/api/usuarios/verificar-token/')
    
    try:
        response = requests.get(url, headers={'Authorization': auth_header}, timeout=5.0)
    except requests.exceptions.Timeout:
        raise ServiceUnavailable('Timeout: El servicio de Gestión tardó demasiado en responder.')
    except requests.exceptions.RequestException:
        raise ServiceUnavailable('Error de conexión con el servicio de Gestión.')

    # Validar código de estado con el HTTP
    if response.status_code in [401, 403]:
        raise exceptions.AuthenticationFailed('Token inválido o expirado.')
    elif response.status_code != 200:
        raise ServiceUnavailable(f'Gestión respondió con error no esperado: {response.status_code}.')

    try:
        data = response.json()
    except ValueError:
        raise ServiceUnavailable('Respuesta inválida (no-JSON) del servicio de Gestión.')
    
    # Extraer datos desde la estructura
    valido = data.get('valido')
    usuario = data.get('usuario', {})
    
    usuario_id = usuario.get('id')
    rol = usuario.get('rol')
    estado = usuario.get('estado')

    if not valido or not usuario_id:
        raise exceptions.AuthenticationFailed('El servicio de Gestión no confirmó un usuario válido.')
    if rol != 'CLIENTE':
        raise exceptions.PermissionDenied('Acceso denegado: Se requiere rol de CLIENTE para esta operación.')
    if estado != 'ACTIVO':
        raise exceptions.PermissionDenied('Acceso denegado: La cuenta del usuario no está ACTIVA.')

    return usuario_id