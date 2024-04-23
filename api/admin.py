from django.contrib import admin
from .models import Ejercicio, RespuestaCorrectaCorta, RespuestaCorrectaLarga


admin.site.register(Ejercicio)
admin.site.register(RespuestaCorrectaCorta)
admin.site.register(RespuestaCorrectaLarga)
