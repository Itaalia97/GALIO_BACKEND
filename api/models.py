from django.db import models
from django.contrib.auth.models import User


class Ejercicio(models.Model):
    numero_pregunta = models.IntegerField()
    pregunta = models.CharField(max_length=2500)

    def __str__(self):
        return self.pregunta

    class Meta:
        app_label = 'api'

class RespuestaUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    respuesta = models.CharField(max_length=3500)

    def __str__(self):
        return f"Respuesta de {self.usuario.username} a '{self.ejercicio.pregunta}'"

    class Meta:
        app_label = 'api'


class RespuestaCorrectaCorta(models.Model):
    ejercicio = models.OneToOneField(Ejercicio, on_delete=models.CASCADE)
    solucion = models.CharField(max_length=255)  # Define un máximo de caracteres para las respuestas cortas

    def __str__(self):
        return f"Solución corta de '{self.ejercicio.pregunta}'"

    class Meta:
        app_label = 'api'

class RespuestaCorrectaLarga(models.Model):
    ejercicio = models.OneToOneField(Ejercicio, on_delete=models.CASCADE)
    solucion = models.TextField()  # Utiliza un campo TextField para permitir respuestas más largas

    def __str__(self):
        return f"Solución larga de '{self.ejercicio.pregunta}'"

    class Meta:
        app_label = 'api'
