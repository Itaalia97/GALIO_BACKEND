from rest_framework import serializers
from .models import Ejercicio, RespuestaUsuario, RespuestaCorrectaCorta, RespuestaCorrectaLarga

class EjercicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ejercicio
        fields = '__all__'

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
