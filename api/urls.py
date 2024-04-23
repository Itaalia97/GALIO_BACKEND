from django.urls import path
from .views import (
    RegistroUsuario,
    EjercicioListCreate,
    RespuestaUsuarioListCreate,
    RespuestaCorrectaCortaListCreate,
RespuestaCorrectaLargaListCreate,
    profile,
    UserListView,
    login_user,
    CustomAuthToken
)

urlpatterns = [
    path('api-token-auth/', CustomAuthToken.as_view()),
    path('registro/', RegistroUsuario.as_view(), name='registro'),
    path('login/', login_user, name='login'),
    path('accounts/profile/', profile, name='profile'),
    path('ejercicios/', EjercicioListCreate.as_view(), name='ejercicio-list-create'),
    path('respuestas_usuario/', RespuestaUsuarioListCreate.as_view(), name='respuesta-usuario-list-create'),
    path('respuestas_correctas_cortas/', RespuestaCorrectaCortaListCreate.as_view(), name='respuesta-correcta-corta-list-create'),
    path('respuestas_correctas_largas/', RespuestaCorrectaLargaListCreate.as_view(), name='respuesta-correcta-larga-list-create'),
    path('users/', UserListView.as_view(), name='user-list'),
]
