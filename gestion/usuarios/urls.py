from django.urls import path
from .views import (
    RegistroUsuarioView,
    LoginView,
    LogoutView,
    ListaUsuariosView,
    DetalleUsuarioView,
    BloquearUsuarioView,
    DesbloquearUsuarioView,
    VerificarTokenView,
)

urlpatterns = [
    path('registro/', RegistroUsuarioView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', ListaUsuariosView.as_view(), name='lista-usuarios'),
    path('<int:pk>/', DetalleUsuarioView.as_view(), name='detalle-usuario'),
    path('<int:pk>/bloquear/', BloquearUsuarioView.as_view(), name='bloquear-usuario'),
    path('<int:pk>/desbloquear/', DesbloquearUsuarioView.as_view(), name='desbloquear-usuario'),
    path('verificar-token/', VerificarTokenView.as_view(), name='verificar-token'),
]