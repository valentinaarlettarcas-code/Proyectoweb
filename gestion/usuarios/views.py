from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from .models import Usuario
from .serializers import RegistroUsuarioSerializer, LoginSerializer, UsuarioSerializer
from .permissions import EsAdministrador

class RegistroUsuarioView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = RegistroUsuarioSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()

        return Response({
            "mensaje": "Cliente registrado correctamente.",
            "usuario": {
                "id": usuario.id,
                "nombre": usuario.first_name,
                "apellido": usuario.last_name,
                "email": usuario.email,
                "rol": usuario.rol,
                "estado": usuario.estado,
            }
        }, status=status.HTTP_201_CREATED)


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
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response(
                {"error": "Usuario no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        if usuario == request.user:
            return Response(
                {"error": "No puedes bloquear tu propia cuenta."},
                status=status.HTTP_403_FORBIDDEN
            )

        if usuario.rol == Usuario.Rol.ADMIN:
            admins_activos = Usuario.objects.filter(
                rol=Usuario.Rol.ADMIN,
                estado=Usuario.Estado.ACTIVO
            ).count()

            if usuario.estado == Usuario.Estado.ACTIVO and admins_activos <= 1:
                return Response(
                    {"error": "No se puede bloquear al último administrador activo."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        usuario.estado = Usuario.Estado.BLOQUEADO
        usuario.save(update_fields=['estado'])

        # Invalida inmediatamente su sesión/token anterior.
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

        usuario.estado = Usuario.Estado.ACTIVO
        usuario.save(update_fields=['estado'])

        return Response({"mensaje": "Usuario desbloqueado correctamente."})