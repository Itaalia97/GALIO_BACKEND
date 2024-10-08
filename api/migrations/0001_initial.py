# Generated by Django 5.0.3 on 2024-03-18 23:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ejercicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pregunta', models.CharField(max_length=500)),
                ('solucion', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='RespuestaCorrecta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('solucion', models.CharField(max_length=500)),
                ('ejercicio', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api.ejercicio')),
            ],
        ),
        migrations.CreateModel(
            name='RespuestaUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('respuesta', models.CharField(max_length=500)),
                ('ejercicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.ejercicio')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
