from rest_framework.permissions import BasePermission
from .models import Usuario


class EsUsuarioActivo(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.estado == Usuario.Estado.ACTIVO
        )


class EsAdministrador(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.estado == Usuario.Estado.ACTIVO
            and request.user.rol == Usuario.Rol.ADMIN
        )


class EsCliente(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.estado == Usuario.Estado.ACTIVO
            and request.user.rol == Usuario.Rol.CLIENTE
        )