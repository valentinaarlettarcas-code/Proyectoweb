from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from .serializers import OrderSerializer

class CrearOrdenView(APIView):
    def post(self, request):
        # Obtenemos el token de seguridad que envió el usuario
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({'error': 'Autenticación requerida. Token no proporcionado.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Validación con microservicio de gestión
        # (Nota: AGREGAR URL REAL PARA ESTE SERVICIO. 
	#---------------------------------------------------------
        
        try:
            # Le enviamos el token a Gestión para que lo valide
            gestion_response = requests.get(gestion_url, headers={'Authorization': auth_header})
            
            if gestion_response.status_code != 200:
                return Response({'error': 'Token inválido o cuenta bloqueada'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Si es válido, extraemos el ID numérico del cliente que nos devuelve Gestión
            cliente_data = gestion_response.json()
            cliente_id = cliente_data.get('cliente_id')
            
        except requests.RequestException:
            # Fallo de comunicación entre microservicios (Regla de negocio: no asumir éxito)
            return Response({'error': 'Servicio de Gestión no disponible'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Para crear la orden
        # Si el token es válido y tenemos el cliente_id,continuamos a validar los datos de la compra
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            # Guardamos la orden, asociando el cliente_id seguro que nos dio Gestión
            serializer.save(cliente_id=cliente_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)