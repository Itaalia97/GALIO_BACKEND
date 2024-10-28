from rest_framework import serializers
from .models import Ejercicio, RespuestaUsuario
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# Serializador para el modelo Ejercicio
class EjercicioSerializer(serializers.ModelSerializer):
    imagen_enunciado_url = serializers.SerializerMethodField()
    imagen_resolucion_url = serializers.SerializerMethodField()

    class Meta:
        model = Ejercicio
        fields = ['id', 'enunciado', 'respuesta_corta', 'resolucion', 'imagen_enunciado_url', 'imagen_resolucion_url']

    def get_imagen_enunciado_url(self, obj):
        request = self.context.get('request')
        if obj.imagen_enunciado:
            return request.build_absolute_uri(obj.imagen_enunciado.url)
        return None

    def get_imagen_resolucion_url(self, obj):
        request = self.context.get('request')
        if obj.imagen_resolucion:
            return request.build_absolute_uri(obj.imagen_resolucion.url)
        return None


# Serializador para el modelo RespuestaUsuario
class RespuestaUsuarioSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField(read_only=True)  # Muestra el nombre del usuario en lugar de solo su ID
    ejercicio = serializers.PrimaryKeyRelatedField(queryset=Ejercicio.objects.all())  # Solo mostrar el ID del ejercicio

    class Meta:
        model = RespuestaUsuario
        fields = ['id', 'usuario', 'ejercicio', 'respuesta_usuario']


# Serializador personalizado para JWT con información adicional
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Agregar el nombre de usuario y correo al token JWT
        token['username'] = user.username
        token['email'] = user.email

        return token
