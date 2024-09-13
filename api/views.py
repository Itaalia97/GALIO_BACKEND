import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.generic import ListView
from django.urls import reverse_lazy
from django.utils import timezone
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



class RegistroUsuario(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registro.html'


@csrf_exempt
def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'Usuario registrado exitosamente'}, status=201)
        else:
            return JsonResponse({'error': form.errors}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


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
