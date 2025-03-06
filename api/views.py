from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import timezone
from django.views import View
from django.views.generic import ListView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics, status
from .models import Ejercicio, RespuestaUsuario
from .serializers import EjercicioSerializer, RespuestaUsuarioSerializer, CustomTokenObtainPairSerializer
from .forms import RegistroUsuarioForm
import json


class SolicitarRecuperacion(View):
    def get(self, request):
        return render(request, 'recuperar_contrasena.html')

class RecuperarContrasena(View):
    def post(self, request):
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'error': 'El correo electrónico no está registrado.'}, status=400)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        link = request.build_absolute_uri(reverse('restablecer_contrasena', kwargs={'uidb64': uid, 'token': token}))
        message = (
            f"Hola {user.username},\n\n"
            "Hemos recibido una solicitud para restablecer la contraseña de tu cuenta de Galio.\n"
            f"Haz clic en el siguiente enlace para restablecer tu contraseña:\n\n"
            f"{link}\n\n"
            "Si no solicitaste este cambio, puedes ignorar este correo.\n"
            "Gracias,\nEl equipo de Galio.")
        send_mail(
            'Restablecer contraseña - Galio',
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,)
        return JsonResponse({'message': 'Se ha enviado un correo electrónico para restablecer la contraseña.'}, status=200)

class RestablecerContrasena(View):
    def get(self, request, uidb64, token):
        return render(request, 'restablecer_contrasena.html', {'uidb64': uidb64, 'token': token})

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            new_password = request.POST.get('new_password')
            user.set_password(new_password)
            user.save()

            return JsonResponse({
                'message': 'Contraseña restablecida exitosamente.',
                'note': (
                    f"Tu nombre de usuario es: **{user.username}**.\n"
                    "Asegúrate de recordarlo, junto con tu nueva contraseña, "
                    "ya que lo necesitarás para iniciar sesión."
                )
            }, status=200)
        else:
            return JsonResponse({'error': 'Token inválido o expirado.'}, status=400)


def home(request):
    return JsonResponse({'message': 'Bienvenido a la API de Ejercicios'})


def list_endpoints(request):
    endpoints = {
        "endpoints": {
            "GET": [
                "/ejercicios/",
                "/registro/",
                "/login/",
                "/recuperar-contrasena/",
                "/accounts/profile/",
                "/respuestas_usuario/",
                "/respuestas_usuarios/<user_id>/",
                "/users/",
            ],
            "POST": [
                "/ejercicios/",
                "/registro/",
                "/login/",
                "/recuperar-contrasena-enviar/",
            ],
        }
    }
    return JsonResponse(endpoints)




class RegistroUsuario(View):
    def get(self, request):
        form = RegistroUsuarioForm()
        return render(request, 'registro.html', {'form': form})

    def post(self, request):
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = User(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email']
            )
            user.set_password(form.cleaned_data['password1'])
            user.save()
            return JsonResponse({'message': 'Usuario registrado exitosamente'}, status=201)
        else:
            return JsonResponse({'error': form.errors}, status=400)


class CustomAuthToken(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user and user.is_active:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            ejercicio_del_dia = Ejercicio.ejercicio_del_dia()

            if ejercicio_del_dia:
                ejercicio_serializer = EjercicioSerializer(ejercicio_del_dia)
                ejercicio_data = ejercicio_serializer.data
            else:
                ejercicio_data = None

            return Response({'token': str(refresh.access_token), 'ejercicio_del_dia': ejercicio_data})
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)


class EjercicioListCreate(generics.ListCreateAPIView):
    queryset = Ejercicio.objects.all()
    serializer_class = EjercicioSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class RespuestaUsuarioListCreate(generics.ListCreateAPIView):
    serializer_class = RespuestaUsuarioSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):
        ejercicio_id = request.data.get('ejercicio')
        if not ejercicio_id:
            return Response({"detail": "ID del ejercicio es requerido."}, status=status.HTTP_400_BAD_REQUEST)
        # Verificar que el ejercicio existe
        try:
            ejercicio = Ejercicio.objects.get(id=ejercicio_id)
        except Ejercicio.DoesNotExist:
            return Response({"detail": "Ejercicio no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        # Verificar si el usuario ya ha enviado una respuesta para este ejercicio
        respuesta_del_dia = RespuestaUsuario.objects.filter(usuario_id=request.user.id, ejercicio=ejercicio).exists()
        if respuesta_del_dia:
            return Response({"detail": "Ya has enviado tu respuesta para este ejercicio."}, status=status.HTTP_400_BAD_REQUEST)
        # Si no ha enviado respuesta, crear la nueva respuesta
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(usuario=request.user, ejercicio=ejercicio)
        # Enviar la respuesta correcta corta
        if ejercicio.respuesta_corta:
            respuesta_correcta_corta = ejercicio.respuesta_corta
        else:
            respuesta_correcta_corta = "No hay respuesta correcta corta disponible para este ejercicio."
        # Construir el mensaje de respuesta con JSON
        response_data = {
            "respuesta_correcta_corta": respuesta_correcta_corta,
            "mensaje": "Respuesta enviada exitosamente."}
        # Devolver el JSON con ensure_ascii=False
        return JsonResponse(json.loads(json.dumps(response_data, ensure_ascii=False)), status=status.HTTP_201_CREATED)


from django.http import JsonResponse
import json
from django.utils import timezone
from rest_framework.views import APIView

class RespuestasUsuarioByDate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        fecha = request.query_params.get('fecha')
        # Verificar si la fecha fue proporcionada
        if not fecha:
            return Response({"detail": "La fecha es requerida."}, status=status.HTTP_400_BAD_REQUEST)
        # Validar el formato de la fecha
        try:
            fecha_parsed = timezone.datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return Response({"detail": "El formato de fecha es inválido. Use AAAA-MM-DD."},
                            status=status.HTTP_400_BAD_REQUEST)
        # Asegurarse de que la fecha no sea futura
        if fecha_parsed >= timezone.now().date():
            return Response({"detail": "No se pueden consultar ejercicios futuros."},
                            status=status.HTTP_400_BAD_REQUEST)
        # Buscar el ejercicio de esa fecha
        ejercicio = Ejercicio.objects.filter(dia=fecha_parsed).first()
        if not ejercicio:
            return Response({"detail": "No hay ejercicio para esta fecha."}, status=status.HTTP_404_NOT_FOUND)
        # Buscar la respuesta del usuario para ese ejercicio
        respuesta_usuario = RespuestaUsuario.objects.filter(usuario=request.user, ejercicio=ejercicio).first()
        if not respuesta_usuario:
            return Response({"detail": "No se ha encontrado una respuesta para esta fecha."},
                            status=status.HTTP_404_NOT_FOUND)
        # Serializar el ejercicio y preparar la respuesta
        ejercicio_serializado = EjercicioSerializer(ejercicio, context={'request': request}).data
        # Construir la respuesta con la información del ejercicio, respuesta del usuario y las imágenes
        response_data = {
            'enunciado': ejercicio.enunciado,
            'imagen_enunciado_url': ejercicio_serializado.get('imagen_enunciado_url'),
            'respuesta_usuario': respuesta_usuario.respuesta_usuario,
            'resolucion': ejercicio.resolucion,
            'imagen_resolucion_url': ejercicio_serializado.get('imagen_resolucion_url'),}
        # Devolver el JSON con ensure_ascii=False para mantener el formato UTF-8
        return JsonResponse(json.loads(json.dumps(response_data, ensure_ascii=False)), status=status.HTTP_200_OK)


class UserListView(ListView):
    model = User
    queryset = User.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        users = list(self.get_queryset().values())
        return JsonResponse(users, safe=False)

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Ejercicio
from .serializers import EjercicioSerializer

class EjercicioDetailView(APIView):
    def get(self, request, ejercicio_id):
        try:
            ejercicio = Ejercicio.objects.get(id=ejercicio_id)
            serializer = EjercicioSerializer(ejercicio)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Ejercicio.DoesNotExist:
            return Response({"detail": "Ejercicio no encontrado."}, status=status.HTTP_404_NOT_FOUND)


@login_required
def profile(request):
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'profile.html', context)


def enviar_correo_prueba(request):
    try:
        send_mail(
            'Asunto de prueba',
            'Este es un correo de prueba.',
            settings.DEFAULT_FROM_EMAIL,
            ['313231562@quimica.unam.mx'],
            fail_silently=False,
        )
        return JsonResponse({'message': 'Correo enviado exitosamente!'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def test_post(request):
    if request.method == 'POST':
        return JsonResponse({"message": "POST request successful!"})
    return JsonResponse({"message": "Only POST requests are allowed!"})


from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from .models import Ejercicio


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            login(request, user)
            today = timezone.now().date()
            ejercicio_del_dia = Ejercicio.objects.filter(dia=today).first()
            if ejercicio_del_dia:
                # Obtener la URL de la imagen del enunciado si existe
                imagen_enunciado_url = None
                if ejercicio_del_dia.imagen_enunciado:
                    imagen_enunciado_url = request.build_absolute_uri(ejercicio_del_dia.imagen_enunciado.url)
                context = {
                    'user_id': user.id,
                    'username': user.username,
                    'id_ejercicio': ejercicio_del_dia.id,
                    'enunciado': ejercicio_del_dia.enunciado,
                    'imagen_enunciado_url': imagen_enunciado_url}
            else:
                context = {
                    'user_id': user.id,
                    'username': user.username,
                    'enunciado': 'Descansa, hoy no hay ejercicio disponible.',
                    'imagen_enunciado_url': None  # No hay imagen si no hay ejercicio
                }
            return JsonResponse(json.loads(json.dumps(context, ensure_ascii=False)))
        else:
            return JsonResponse({'error': 'Credenciales inválidas'}, status=401)
    else:
        return render(request, 'login.html')


from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import RespuestaUsuario, User


# Función para calcular la racha correctamente
def calcular_racha_respuestas(usuario):
    respuestas = RespuestaUsuario.objects.filter(usuario=usuario).order_by('-fecha_envio')

    if not respuestas:
        return 0

    racha = 1
    hoy = timezone.now().date()

    # Si la última respuesta no es de hoy o del último día hábil, racha se resetea a 0
    if respuestas[0].fecha_envio < obtener_ultimo_dia_habil():
        return 0

    for i in range(1, len(respuestas)):
        dia_actual = respuestas[i - 1].fecha_envio
        dia_anterior = respuestas[i].fecha_envio

        # Solo contar días hábiles (lunes a viernes)
        if dia_actual - timedelta(days=1) != dia_anterior and not es_fin_de_semana(dia_actual - timedelta(days=1)):
            break  # Se interrumpió la racha
        racha += 1

    return racha


# Función para obtener el último día hábil (excluyendo fines de semana)
def obtener_ultimo_dia_habil():
    hoy = timezone.now().date()
    if hoy.weekday() == 0:  # Si es lunes, el último hábil fue el viernes
        return hoy - timedelta(days=3)
    elif hoy.weekday() in [6]:  # Si es domingo, el último hábil fue el viernes
        return hoy - timedelta(days=2)
    else:
        return hoy - timedelta(days=1)  # Si es otro día, el anterior fue el último hábil


# Función para saber si una fecha es fin de semana
def es_fin_de_semana(fecha):
    return fecha.weekday() in [5, 6]  # 5 = Sábado, 6 = Domingo


# Vista del tablero de posiciones
class LeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        respuestas_agrupadas = RespuestaUsuario.objects.values('usuario').annotate(total_respuestas=Count('id'))

        # Lista de usuarios con rachas activas
        rachas = []
        for user_data in respuestas_agrupadas:
            user = User.objects.get(id=user_data['usuario'])
            racha = calcular_racha_respuestas(user)

            # 🔹 Solo agregar usuarios con una racha mayor a 0
            if racha > 0:
                rachas.append((user, racha, user_data['total_respuestas']))

        # Ordenar por racha descendente y seleccionar los primeros 20
        top_20_racha = sorted(rachas, key=lambda x: x[1], reverse=True)[:20]
        # Ordenar por total de respuestas enviadas y seleccionar los primeros 20
        top_20_totales = sorted(rachas, key=lambda x: x[2], reverse=True)[:20]

        # Encontrar la posición del usuario logueado
        usuario_logeado = request.user
        posicion_racha = next((i for i, r in enumerate(top_20_racha) if r[0] == usuario_logeado), None)
        posicion_totales = next((i for i, r in enumerate(top_20_totales) if r[0] == usuario_logeado), None)

        # Construir la respuesta JSON ajustada
        respuesta = {
            'top_20_racha': [
                {'posicion': i + 1, 'usuario': r[0].username, 'racha': r[1]}
                for i, r in enumerate(top_20_racha)
            ],
            'usuario_logeado_racha': {
                'posicion': posicion_racha + 1 if posicion_racha is not None else None,
                'usuario': usuario_logeado.username,
                'racha': calcular_racha_respuestas(usuario_logeado)
            },
            'top_20_totales': [
                {'posicion': i + 1, 'usuario': r[0].username, 'total_ejercicios': r[2]}
                for i, r in enumerate(top_20_totales)
            ],
            'usuario_logeado_totales': {
                'posicion': posicion_totales + 1 if posicion_totales is not None else None,
                'usuario': usuario_logeado.username,
                'total_ejercicios': RespuestaUsuario.objects.filter(usuario=usuario_logeado).count()
            }
        }

        return Response(respuesta, status=200)