# api/forms.py
import re
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class RegistroUsuarioForm(forms.Form):
    email = forms.EmailField(required=True, label='Correo electrónico')
    username = forms.CharField(required=True, label='Nombre de usuario', max_length=50)
    password1 = forms.CharField(widget=forms.PasswordInput, label='Contraseña')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirmar contraseña')

    def clean_username(self):
        username = self.cleaned_data.get('username')

        # Expresión regular para permitir letras, números, espacios y caracteres especiales
        if not re.match(r'^[\w\sñáéíóúü]+$', username):
            raise ValidationError(
                "El nombre de usuario solo puede contener letras, números, espacios y caracteres especiales.")

        if User.objects.filter(username=username).exists():
            raise ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden.")