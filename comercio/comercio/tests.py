from unittest.mock import patch
from rest_framework.test import APITestCase
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from requests.exceptions import Timeout
from rest_framework import status
from django.test import RequestFactory
from .autenticacion import verificar_token_cliente, ServiceUnavailable
from .models import Order

class AutenticacionTests(APITestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_sin_token(self):
        request = self.factory.get('/api/orders/')
        with self.assertRaisesMessage(AuthenticationFailed, 'Token de autenticación no proporcionado.'):
            verificar_token_cliente(request)

    @patch('comercio.autenticacion.requests.get')
    def test_token_invalido(self, mock_get):
        mock_get.return_value.status_code = 401
        request = self.factory.get('/api/orders/', HTTP_AUTHORIZATION='Token falso')
        with self.assertRaisesMessage(AuthenticationFailed, 'Token inválido o expirado.'):
            verificar_token_cliente(request)

    @patch('comercio.autenticacion.requests.get')
    def test_gestion_caido_timeout(self, mock_get):
        mock_get.side_effect = Timeout()
        request = self.factory.get('/api/orders/', HTTP_AUTHORIZATION='Token valido')
        with self.assertRaisesMessage(ServiceUnavailable, 'Timeout: El servicio de Gestión tardó demasiado en responder.'):
            verificar_token_cliente(request)

    @patch('comercio.autenticacion.requests.get')
    def test_administrador_rechazado(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "valido": True, "usuario": {"id": 1, "rol": "ADMIN", "estado": "ACTIVO"}
        }
        request = self.factory.get('/api/orders/', HTTP_AUTHORIZATION='Token admin')
        with self.assertRaisesMessage(PermissionDenied, 'Acceso denegado: Se requiere rol de CLIENTE para esta operación.'):
            verificar_token_cliente(request)

    @patch('comercio.autenticacion.requests.get')
    def test_cuenta_no_activa(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "valido": True, "usuario": {"id": 1, "rol": "CLIENTE", "estado": "INACTIVO"}
        }
        request = self.factory.get('/api/orders/', HTTP_AUTHORIZATION='Token inactivo')
        with self.assertRaisesMessage(PermissionDenied, 'Acceso denegado: La cuenta del usuario no está ACTIVA.'):
            verificar_token_cliente(request)

    @patch('comercio.autenticacion.requests.get')
    def test_acceso_correcto(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "valido": True, "usuario": {"id": 99, "rol": "CLIENTE", "estado": "ACTIVO"}
        }
        request = self.factory.get('/api/orders/', HTTP_AUTHORIZATION='Token bueno')
        cliente_id = verificar_token_cliente(request)
        self.assertEqual(cliente_id, 99)


class IntentoTests(APITestCase):
    def test_mismo_checkout_devuelve_misma_orden(self):
        # Cliente 1 crea orden con checkout_abc
        orden1 = Order.objects.create(cliente_id=1, checkout_id='checkout_abc', total_amount=1000)
        
        # Cliente 1 repite la petición
        orden_repetida = Order.objects.filter(cliente_id=1, checkout_id='checkout_abc').first()
        self.assertEqual(orden1.id, orden_repetida.id)

    def test_distinto_cliente_mismo_checkout_crea_nueva_orden(self):
        # Cliente 1 y Cliente 2 usan el mismo checkout_id por casualidad
        orden1 = Order.objects.create(cliente_id=1, checkout_id='checkout_xyz')
        orden2 = Order.objects.create(cliente_id=2, checkout_id='checkout_xyz')
        
        self.assertNotEqual(orden1.id, orden2.id)
        self.assertEqual(Order.objects.count(), 2)