from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.generic import ListView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import generics, status
from django.urls import reverse_lazy
from django.views import generic
from .models import Ejercicio, RespuestaUsuario, RespuestaCorrectaCorta, RespuestaCorrectaLarga
from .serializers import EjercicioSerializer, RespuestaUsuarioSerializer, RespuestaCorrectaCortaSerializer, RespuestaCorrectaLargaSerializer


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


class CustomAuthToken(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({'token': str(refresh.access_token)})
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)


class EjercicioListCreate(generics.ListCreateAPIView):
    queryset = Ejercicio.objects.all()
    serializer_class = EjercicioSerializer


class RespuestaUsuarioListCreate(generics.ListCreateAPIView):
    queryset = RespuestaUsuario.objects.all()
    serializer_class = RespuestaUsuarioSerializer


class RespuestaCorrectaCortaListCreate(generics.ListCreateAPIView):
    queryset = RespuestaCorrectaCorta.objects.all()
    serializer_class = RespuestaCorrectaCortaSerializer


class RespuestaCorrectaLargaListCreate(generics.ListCreateAPIView):
    queryset = RespuestaCorrectaLarga.objects.all()
    serializer_class = RespuestaCorrectaLargaSerializer


class UserListView(ListView):
    model = User
    queryset = User.objects.all()
    authentication_classes = (TokenAuthentication,)
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


#@csrf_protect
@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')  # Redirigir al usuario al perfil
        else:
            return redirect('registro')  # Redirigir al usuario al registro si las credenciales son inválidas
    else:
        return render(request, 'login.html')
