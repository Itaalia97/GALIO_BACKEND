import json
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.http import JsonResponse, HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.generic import ListView
from django.views import generic
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework import generics, status
from .models import Ejercicio, RespuestaUsuario, RespuestaCorrectaCorta, RespuestaCorrectaLarga
from .serializers import EjercicioSerializer, RespuestaUsuarioSerializer, RespuestaCorrectaCortaSerializer, RespuestaCorrectaLargaSerializer, CustomTokenObtainPairSerializer
from .forms import RegistroUsuarioForm


class SolicitarRecuperacion(View):
    def get(self, request):
        return render(request, 'recuperar_contrasena.html')  # Renderiza el formulario para solicitar recuperación

class RecuperarContrasena(View):
    def post(self, request):
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'error': 'El correo electrónico no está registrado.'}, status=400)

        # Generar el token y la URL
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        link = request.build_absolute_uri(reverse('restablecer_contrasena', kwargs={'uidb64': uid, 'token': token}))

        # Crear un mensaje más amigable
        message = (
            f"Hola {user.username},\n\n"
            "Hemos recibido una solicitud para restablecer la contraseña de tu cuenta de Galio.\n"
            f"Haz clic en el siguiente enlace para restablecer tu contraseña:\n\n"
            f"{link}\n\n"
            "Si no solicitaste este cambio, puedes ignorar este correo.\n"
            "Gracias,\nEl equipo de Galio."
        )

        # Enviar el correo
        send_mail(
            'Restablecer contraseña - Galio',
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return JsonResponse({'message': 'Se ha enviado un correo electrónico para restablecer la contraseña.'}, status=200)

class RestablecerContrasena(View):
    def get(self, request, uidb64, token):
        # Mostrar el formulario para restablecer la contraseña
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
            return JsonResponse({'message': 'Contraseña restablecida exitosamente.'}, status=200)
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
                "/recuperar-contrasena/",  # Para mostrar el formulario de recuperación
                "/accounts/profile/",
                "/respuestas_usuario/",
                "/respuestas_usuarios/<user_id>/",
                "/respuestas_correctas_cortas/",
                "/respuestas_correctas_largas/",
                "/users/",
            ],
            "POST": [
                "/ejercicios/",
                "/registro/",
                "/login/",
                "/recuperar-contrasena-enviar/",  # Para manejar el envío del correo de recuperación
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
        if user:
            login(request, user)
            refresh = RefreshToken.for_user(user)

            # Obtener el ejercicio del día
            ejercicio_del_dia = Ejercicio.ejercicio_del_dia()

            # Serializar el ejercicio del día
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


class RespuestaUsuarioList(generics.ListCreateAPIView):
    serializer_class = RespuestaUsuarioSerializer


    def get_ejercicio_del_dia(self):
        today = timezone.now().date()
        return Ejercicio.objects.filter(fecha__date=today).first()



    def list(self, request, *args, **kwargs):
        ejercicio_del_dia = self.get_ejercicio_del_dia()

        if not ejercicio_del_dia:
            return Response({"detail": "No hay ejercicio disponible para hoy"}, status=status.HTTP_404_NOT_FOUND)

        respuesta_del_dia = RespuestaUsuario.objects.filter(usuario=request.user, ejercicio=ejercicio_del_dia).first()
        if respuesta_del_dia:
            return Response({"detail": "Ya has enviado tu respuesta para hoy"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(ejercicio_del_dia)
        return Response(serializer.data)



    def create(self, request, *args, **kwargs):
        ejercicio_del_dia = self.get_ejercicio_del_dia()

        if not ejercicio_del_dia:
            return Response({"detail": "No hay ejercicio disponible para hoy"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(usuario=request.user, ejercicio=ejercicio_del_dia)

        respuesta_correcta_corta = RespuestaCorrectaCorta.objects.filter(ejercicio=ejercicio_del_dia).first()
        respuesta_correcta_serializer = RespuestaCorrectaCortaSerializer(respuesta_correcta_corta)

        return Response({
            "respuesta_correcta_corta": respuesta_correcta_serializer.data
        }, status=status.HTTP_201_CREATED)


class RespuestasUsuarioList(generics.ListAPIView):
    serializer_class = RespuestaUsuarioSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return RespuestaUsuario.objects.filter(usuario_id=user_id)

class RespuestasUsuarioList(generics.ListAPIView):
    serializer_class = RespuestaUsuarioSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return RespuestaUsuario.objects.filter(usuario_id=user_id)

class RespuestaCorrectaCortaListCreate(generics.ListCreateAPIView):
    queryset = RespuestaCorrectaCorta.objects.all()
    serializer_class = RespuestaCorrectaCortaSerializer


class RespuestaCorrectaLargaListCreate(generics.ListCreateAPIView):
    queryset = RespuestaCorrectaLarga.objects.all()
    serializer_class = RespuestaCorrectaLargaSerializer


class UserListView(ListView):
    model = User
    queryset = User.objects.all()
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        users = list(self.get_queryset().values())
        return JsonResponse(users, safe=False)


@login_required
def profile(request):
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'profile.html', context)


@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            today = timezone.now().date()
            ejercicio_del_dia = Ejercicio.objects.filter(fecha__date=today).first()
            if ejercicio_del_dia:
                context = {
                    'user_id': user.id,
                    'username': user.username,
                    'id_pregunta': ejercicio_del_dia.numero_pregunta,
                    'enunciado': ejercicio_del_dia.pregunta
                }
            else:
                context = {
                    'user_id': user.id,
                    'username': user.username,
                    'enunciado': 'Descansa, hoy no hay ejercicio disponible'
                }
            return JsonResponse(context)
        else:
            print("Credenciales inválidas.")
            return JsonResponse({'error': 'Credenciales inválidas'}, status=401)
    else:
        return render(request, 'login.html')

from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings

def enviar_correo_prueba(request):
    try:
        send_mail(
            'Asunto de prueba',
            'Este es un correo de prueba.',
            settings.DEFAULT_FROM_EMAIL,
            ['313231562@quimica.unam.mx'],  # Cambia esto por tu correo
            fail_silently=False,
        )
        return JsonResponse({'message': 'Correo enviado exitosamente!'}, status=200)
    except Exception as e:
        print(f"Error al enviar correo: {e}")  # Imprimir el error en la consola
        return JsonResponse({'error': str(e)}, status=500)



# views.py

import json
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, status
from .models import Ejercicio, RespuestaUsuario, RespuestaCorrectaCorta, RespuestaCorrectaLarga
from .serializers import EjercicioSerializer, RespuestaUsuarioSerializer, RespuestaCorrectaCortaSerializer, RespuestaCorrectaLargaSerializer, CustomTokenObtainPairSerializer
from .forms import RegistroUsuarioForm


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
            "Gracias,\nEl equipo de Galio."
        )

        send_mail(
            'Restablecer contraseña - Galio',
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

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
            return JsonResponse({'message': 'Contraseña restablecida exitosamente.'}, status=200)
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
                "/respuestas_correctas_cortas/",
                "/respuestas_correctas_largas/",
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


class RespuestaUsuarioListCreate(generics.ListCreateAPIView):
    serializer_class = RespuestaUsuarioSerializer

    def create(self, request, *args, **kwargs):
        # Obtener el ID del ejercicio de la solicitud
        ejercicio_id = request.data.get('id_ejercicio')
        if not ejercicio_id:
            return Response({"detail": "ID del ejercicio es requerido."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar que el ejercicio existe
        try:
            ejercicio = Ejercicio.objects.get(id_ejercicio=ejercicio_id)
        except Ejercicio.DoesNotExist:
            return Response({"detail": "Ejercicio no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Verificar si el usuario ya ha enviado una respuesta para este ejercicio
        respuesta_del_dia = RespuestaUsuario.objects.filter(usuario_id=request.user, ejercicio=ejercicio).exists()
        if respuesta_del_dia:
            return Response({"detail": "Ya has enviado tu respuesta para este ejercicio."}, status=status.HTTP_400_BAD_REQUEST)

        # Si no ha enviado respuesta, crear la nueva respuesta
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(usuario_id=request.user, ejercicio=ejercicio)

        # Enviar la respuesta correcta corta (opcional)
        respuesta_correcta_corta = RespuestaCorrectaCorta.objects.filter(ejercicio=ejercicio).first()
        respuesta_correcta_serializer = RespuestaCorrectaCortaSerializer(respuesta_correcta_corta)

        return Response({
            "respuesta_correcta_corta": respuesta_correcta_serializer.data
        }, status=status.HTTP_201_CREATED)


class RespuestaCorrectaCortaListCreate(generics.ListCreateAPIView):
    queryset = RespuestaCorrectaCorta.objects.all()
    serializer_class = RespuestaCorrectaCortaSerializer


class RespuestaCorrectaLargaListCreate(generics.ListCreateAPIView):
    queryset = RespuestaCorrectaLarga.objects.all()
    serializer_class = RespuestaCorrectaLargaSerializer


class RespuestasUsuarioList(generics.ListAPIView):
    serializer_class = RespuestaUsuarioSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return RespuestaUsuario.objects.filter(usuario_id=user_id)


class UserListView(ListView):
    model = User
    queryset = User.objects.all()
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        users = list(self.get_queryset().values())
        return JsonResponse(users, safe=False)


@login_required
def profile(request):
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'profile.html', context)


@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            login(request, user)
            today = timezone.now().date()
            ejercicio_del_dia = Ejercicio.objects.filter(fecha__date=today).first()
            if ejercicio_del_dia:
                context = {
                    'user_id': user.id,
                    'username': user.username,
                    'id_ejercicio': ejercicio_del_dia.id_ejercicio,
                    'enunciado': ejercicio_del_dia.ejercicio
                }
            else:
                context = {
                    'user_id': user.id,
                    'username': user.username,
                    'enunciado': 'Descansa, hoy no hay ejercicio disponible'
                }
            return JsonResponse(context)
        else:
            return JsonResponse({'error': 'Credenciales inválidas'}, status=401)
    else:
        return render(request, 'login.html')


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

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def test_post(request):
    if request.method == 'POST':
        return JsonResponse({"message": "POST request successful!"})
    return JsonResponse({"message": "Only POST requests are allowed!"})
