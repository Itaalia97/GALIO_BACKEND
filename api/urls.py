from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegistroUsuario,
    EjercicioListCreate,
    RespuestaUsuarioList,
    RespuestasUsuarioList,
    RespuestaCorrectaCortaListCreate,
    RespuestaCorrectaLargaListCreate,
    profile,
    UserListView,
    login_user,
    CustomAuthToken
)

urlpatterns = [
    path('api-token-auth/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('registro/', csrf_exempt(RegistroUsuario.as_view()), name='registro'),
    path('login/', csrf_exempt(login_user), name='login'),
    path('accounts/profile/', csrf_exempt(profile), name='profile'),
    path('ejercicios/', csrf_exempt(EjercicioListCreate.as_view()), name='ejercicio-list-create'),
    path('respuestas_usuario/', csrf_exempt(RespuestaUsuarioList.as_view()), name='respuesta-usuario-list-create'),
    path('respuestas_usuarios/<int:user_id>/', csrf_exempt(RespuestasUsuarioList.as_view()), name='respuestas-usuario-list'),
    path('respuestas_correctas_cortas/', csrf_exempt(RespuestaCorrectaCortaListCreate.as_view()), name='respuesta-correcta-corta-list-create'),
    path('respuestas_correctas_largas/', csrf_exempt(RespuestaCorrectaLargaListCreate.as_view()), name='respuesta-correcta-larga-list-create'),
    path('users/', UserListView.as_view(), name='user-list'),
]
