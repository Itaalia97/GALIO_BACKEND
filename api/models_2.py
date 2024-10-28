from django.db import models
from django.contrib.auth.models import User  # Verifica que estás utilizando el modelo User correcto (Django 3.x o superior puede requerir un ajuste)
from django.utils import timezone

# Modelo Ejercicio
class Ejercicio(models.Model):
    id_ejercicio = models.AutoField(primary_key=True)  # Campo de ID automático
    ejercicio = models.CharField(max_length=2500)  # Texto del ejercicio
    fecha = models.DateTimeField(default=timezone.now)  # Fecha del ejercicio

    def __str__(self):
        return self.ejercicio

    @classmethod
    def ejercicio_del_dia(cls):
        today = timezone.now().date()
        # Obtenemos el primer ejercicio del día actual
        ejercicio_del_dia = cls.objects.filter(fecha__date=today).first()
        return ejercicio_del_dia


# Modelo RespuestaUsuario
class RespuestaUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="respuestas")  # Relación con el modelo User
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE, related_name="respuestas_usuario")  # Relación con el modelo Ejercicio
    respuesta_usuario = models.CharField(max_length=3500)  # Texto de la respuesta del usuario

    def __str__(self):
        # Mostramos los primeros 50 caracteres de la respuesta del usuario
        return f"Respuesta de {self.usuario.username} a '{self.respuesta_usuario[:50]}...'"

    class Meta:
        app_label = 'api'  # Asegura que está en la app 'api'


# Modelo RespuestaCorrectaCorta
class RespuestaCorrectaCorta(models.Model):
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE, related_name="respuestas_cortas")  # Relación con el modelo Ejercicio
    respuesta_correcta_corta = models.CharField(max_length=255)  # Texto de la respuesta correcta corta

    def __str__(self):
        return f"Respuesta correcta corta: {self.respuesta_correcta_corta}"

    class Meta:
        app_label = 'api'


# Modelo RespuestaCorrectaLarga
class RespuestaCorrectaLarga(models.Model):
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE, related_name="respuestas_largas")  # Relación con el modelo Ejercicio
    respuesta_correcta_larga = models.TextField()  # Texto de la respuesta correcta larga

    def __str__(self):
        # Mostramos solo los primeros 50 caracteres de la respuesta larga
        return f"Respuesta correcta larga: {self.respuesta_correcta_larga[:50]}..."

    class Meta:
        app_label = 'api'
