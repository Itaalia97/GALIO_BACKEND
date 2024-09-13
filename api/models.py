from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Ejercicio(models.Model):
    numero_pregunta = models.IntegerField()
    pregunta = models.CharField(max_length=2500)
    fecha = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.pregunta

    @classmethod
    def ejercicio_del_dia(cls):
        today = timezone.now().date()
        ejercicio_del_dia = cls.objects.filter(fecha__date=today).first()
        return ejercicio_del_dia


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
    solucion = models.CharField(max_length=255)

    def __str__(self):
        return f"Solución corta de '{self.ejercicio.pregunta}'"

    class Meta:
        app_label = 'api'

class RespuestaCorrectaLarga(models.Model):
    ejercicio = models.OneToOneField(Ejercicio, on_delete=models.CASCADE)
    solucion = models.TextField()

    def __str__(self):
        return f"Solución larga de '{self.ejercicio.pregunta}'"

    class Meta:
        app_label = 'api'
