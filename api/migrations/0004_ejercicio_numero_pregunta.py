# Generated by Django 5.0.3 on 2024-04-16 00:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_delete_pregunta_remove_ejercicio_solucion'),
    ]

    operations = [
        migrations.AddField(
            model_name='ejercicio',
            name='numero_pregunta',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
