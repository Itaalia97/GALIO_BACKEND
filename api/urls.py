from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegistroUsuario,
    EjercicioListCreate,
    EjercicioDetailView,
    RespuestaUsuarioListCreate,
    RespuestasUsuarioByDate,
    profile,
    UserListView,
    login_user,
    CustomAuthToken,
    home,
    list_endpoints,
    RecuperarContrasena,
    RestablecerContrasena,
    SolicitarRecuperacion,
    enviar_correo_prueba,
    LeaderboardView
)

urlpatterns = [
    # Sección: Home y lista de endpoints
    path('', list_endpoints, name='list-endpoints'),
    path('home/', home, name='home'),

    # Sección: Autenticación
    path('api-token-auth/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', login_user, name='login'),
    path('accounts/profile/', profile, name='profile'),

    # Sección: Registro de usuarios
    path('registro/', RegistroUsuario.as_view(), name='registro'),

    # Sección: Ejercicios y respuestas
    path('ejercicios/', EjercicioListCreate.as_view(), name='ejercicio-list-create'),
    path('respuesta_usuario/', RespuestaUsuarioListCreate.as_view(), name='respuesta_usuario'),
    path('ejercicios/<int:ejercicio_id>/', EjercicioDetailView.as_view(), name='ejercicio-detail'),
    path('respuestas_usuario_fecha/', RespuestasUsuarioByDate.as_view(), name='respuestas_usuario_fecha'),

    #Sección: Tablero de posiciones
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),

    # Sección: Usuarios
    path('users/', UserListView.as_view(), name='user-list'),

    # Sección: Recuperación de contraseñas
    path('solicitar-recuperacion/', SolicitarRecuperacion.as_view(), name='solicitar_recuperacion'),
    path('recuperar-contrasena-enviar/', RecuperarContrasena.as_view(), name='recuperar_contrasena'),
    path('restablecer-contrasena/<uidb64>/<token>/', RestablecerContrasena.as_view(), name='restablecer_contrasena'),

    # Sección: Envío de correo de prueba
    path('enviar-correo-prueba/', enviar_correo_prueba, name='enviar_correo_prueba'),
]

# Añadir la siguiente línea solo en desarrollo (DEBUG = True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)