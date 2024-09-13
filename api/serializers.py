from rest_framework import serializers
from .models import Ejercicio, RespuestaUsuario, RespuestaCorrectaCorta, RespuestaCorrectaLarga
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Agregar claims personalizados si es necesario
        token['username'] = user.username
        return token


class EjercicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ejercicio
        fields = ['id', 'numero_pregunta', 'pregunta', 'fecha']


class RespuestaUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestaUsuario
        fields = '__all__'

class RespuestaCorrectaCortaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestaCorrectaCorta
        fields = '__all__'

class RespuestaCorrectaLargaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestaCorrectaLarga
        fields = '__all__'
