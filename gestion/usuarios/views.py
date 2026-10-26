import hashlib
import secrets
from datetime import timedelta

from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Usuario, TokenActivacion
from .permissions import EsAdministrador
from .serializers import (
    LoginSerializer,
    RegistroUsuarioSerializer,
    UsuarioSerializer,
)

class RegistroUsuarioView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = RegistroUsuarioSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            usuario = serializer.save()
            usuario.estado = Usuario.Estado.PENDIENTE
            usuario.is_active = False
            usuario.save(update_fields=["estado", "is_active"])

            token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(token.encode()).hexdigest()

            TokenActivacion.objects.create(
                usuario=usuario,
                token_hash=token_hash
            )

            enlace = request.build_absolute_uri(
                reverse("activar-usuario", args=[token])
            )

            send_mail(
                "Activa tu cuenta",
                f"Activa tu cuenta mediante este enlace:\n{enlace}\n"
                "El enlace caduca en 24 horas.",
                settings.DEFAULT_FROM_EMAIL,
                [usuario.email],
                fail_silently=False
            )

        return Response({
            "mensaje": "Registro realizado. Revisa tu correo para activar la cuenta."
        }, status=status.HTTP_201_CREATED)

class ActivarUsuarioView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        with transaction.atomic():
            try:
                activacion = TokenActivacion.objects.select_for_update().get(
                    token_hash=token_hash
                )
            except TokenActivacion.DoesNotExist:
                return Response(
                    {"error": "Enlace no válido."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if activacion.usado:
                return Response(
                    {"error": "Este enlace ya fue utilizado."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if timezone.now() > activacion.creado + timedelta(hours=24):
                return Response(
                    {"error": "El enlace ha caducado."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            usuario = Usuario.objects.select_for_update().get(
                pk=activacion.usuario_id
            )

            if usuario.estado != Usuario.Estado.PENDIENTE:
                return Response(
                    {"error": "La cuenta no está pendiente de activación."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            usuario.estado = Usuario.Estado.ACTIVO
            usuario.is_active = True
            usuario.save(update_fields=["estado", "is_active"])

            activacion.usado = True
            activacion.save(update_fields=["usado"])

        return Response({
            "mensaje": "Cuenta activada correctamente."
        })
        
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        usuario = serializer.validated_data['usuario']

        Token.objects.filter(user=usuario).delete()
        token = Token.objects.create(user=usuario)

        return Response({
            "mensaje": "Inicio de sesión correcto.",
            "token": token.key,
            "usuario": {
                "id": usuario.id,
                "nombre": usuario.first_name,
                "apellido": usuario.last_name,
                "email": usuario.email,
                "rol": usuario.rol,
                "estado": usuario.estado,
            }
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()

        return Response({
            "mensaje": "Sesión cerrada correctamente."
        })

class ListaUsuariosView(generics.ListAPIView):
    queryset = Usuario.objects.all().order_by('id')
    serializer_class = UsuarioSerializer
    permission_classes = [EsAdministrador]


class DetalleUsuarioView(generics.RetrieveUpdateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [EsAdministrador]

    def update(self, request, *args, **kwargs):
        usuario = self.get_object()

        if usuario == request.user:
            return Response(
                {"error": "No puedes editar tu propio usuario."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)


class BloquearUsuarioView(APIView):
    permission_classes = [EsAdministrador]

    def post(self, request, pk):

        with transaction.atomic():
            try:
                usuario = Usuario.objects.get(pk=pk)
            except Usuario.DoesNotExist:
                return Response(
                    {"error": "Usuario no encontrado."},
                    status=status.HTTP_404_NOT_FOUND
                )

            if usuario.pk == request.user.pk:
                return Response(
                    {"error": "No puedes bloquear tu propia cuenta."},
                    status=status.HTTP_403_FORBIDDEN
                )

            if usuario.rol == Usuario.Rol.ADMIN:
                # Bloqueamos todos los administradores en orden estable.
                # Esto serializa los bloqueos concurrentes de admins.
                administradores = list(
                    Usuario.objects.select_for_update()
                    .filter(rol=Usuario.Rol.ADMIN)
                    .order_by("pk")
                )

                usuario = next(
                    admin for admin in administradores
                    if admin.pk == pk
                )

                activos = sum(
                    admin.estado == Usuario.Estado.ACTIVO
                    for admin in administradores
                )

                if usuario.estado == Usuario.Estado.ACTIVO and activos <= 1:
                    return Response(
                        {"error": "No se puede bloquear al ultimo administrador activo."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                usuario = Usuario.objects.select_for_update().get(pk=pk)

            usuario.estado = Usuario.Estado.BLOQUEADO
            usuario.save(update_fields=["estado"])

            # Invalidar el token en la misma transaccion.
            Token.objects.filter(user=usuario).delete()

        return Response({"mensaje": "Usuario bloqueado correctamente."})

class DesbloquearUsuarioView(APIView):
    permission_classes = [EsAdministrador]

    def post(self, request, pk):
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response(
                {"error": "Usuario no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        if usuario.estado == Usuario.Estado.BLOQUEADO:
            if usuario.is_active:
                usuario.estado = Usuario.Estado.ACTIVO
                usuario.save(update_fields=["estado"])

                return Response({
                    "mensaje": "Usuario desbloqueado correctamente."
                })
            else:
                return Response(
                    {"error": "La cuenta nunca ha sido activada."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"error": "Solo se pueden desbloquear usuarios bloqueados."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
class VerificarTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario = request.user

        if usuario.estado != Usuario.Estado.ACTIVO:
            return Response(
                {"valido": False, "error": "Usuario no activo."},
                status=status.HTTP_403_FORBIDDEN
            )

        return Response({
            "valido": True,
            "usuario": {
                "id": usuario.id,
                "email": usuario.email,
                "rol": usuario.rol,
                "estado": usuario.estado,
            }
        })


