from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Modelo para los ejercicios
class Ejercicio(models.Model):
    id = models.AutoField(primary_key=True)
    dia = models.DateField(default=timezone.now)  # Fecha del ejercicio
    enunciado = models.TextField()  # El enunciado del ejercicio
    imagen_enunciado = models.ImageField(upload_to='enunciados/', null=True, blank=True)  # Imagen opcional para el enunciado
    respuesta_corta = models.CharField(max_length=255)  # Respuesta corta del ejercicio
    resolucion = models.TextField()  # Resolución o respuesta larga del ejercicio
    imagen_resolucion = models.ImageField(upload_to='resoluciones/', null=True, blank=True)  # Imagen opcional para la resolución
    def __str__(self):
        return f"Ejercicio del {self.dia} - {self.enunciado[:50]}..."

# Modelo para registrar las respuestas del usuario
class RespuestaUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="respuestas")  # Relación con el usuario
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE, related_name="respuestas_usuario")  # Relación con el ejercicio
    respuesta_usuario = models.CharField(max_length=3500)  # Respuesta del usuario
    fecha_envio = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Respuesta de {self.usuario.username} a '{self.respuesta_usuario[:50]}...'"
