import os
import django
from django.core.management.base import BaseCommand
from api.models import Ejercicio

class Command(BaseCommand):
    help = 'Elimina todos los ejercicios de la base de datos'

    def handle(self, *args, **kwargs):
        # Configurar Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'galio.settings')
        django.setup()

        # Eliminar todos los ejercicios
        Ejercicio.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Se eliminaron todos los ejercicios correctamente'))
