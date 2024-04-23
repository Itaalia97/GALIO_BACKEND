import os
import django
import re
from docx import Document as DocxDocument

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'galio.settings')
django.setup()

# Obtener la ruta absoluta del archivo DOCX
docx_file_path = "D:\\Personal\\Desktop\\GALIO\\api\\solopreguntas.docx"
print(docx_file_path)

# Verificar si el archivo DOCX existe
if not os.path.exists(docx_file_path):
    print("El archivo DOCX no existe.")
    exit()

# Leer el contenido del archivo DOCX y convertirlo a texto plano
try:
    docx = DocxDocument(docx_file_path)
    plain_text = ""
    for paragraph in docx.paragraphs:
        plain_text += paragraph.text + "\n"
except Exception as e:
    print("Error al leer el archivo DOCX:", e)
    exit()

# Extraer las preguntas del texto plano manteniendo su número y enunciado
preguntas = re.findall(r'(\d+\.\s*.*?)\s*(?=\d+\.)', plain_text, re.DOTALL)

# Crear instancias de modelos y guardar en la base de datos
from api.models import Ejercicio
from django.db import transaction

with transaction.atomic():
    for pregunta_texto in preguntas:
        pregunta_texto = pregunta_texto.strip()
        if pregunta_texto:  # Verificar que la pregunta no esté vacía
            # Obtener el número y la pregunta
            numero, enunciado = pregunta_texto.split(".", 1)
            numero = int(numero.strip())  # Convertir el número a entero
            enunciado = enunciado.strip()
            pregunta = Ejercicio(numero=numero, pregunta=enunciado)
            pregunta.save()
