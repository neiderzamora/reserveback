# Generated by Django 4.2 on 2023-05-25 15:30

import datetime
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Campus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Viva', 'Viva'), ('El_Trapiche', 'El Trapiche')], max_length=50, unique=True)),
                ('capacity', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='TimeSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('duration', models.DurationField()),
                ('max_capacity', models.IntegerField(default=30)),
                ('current_capacity', models.IntegerField(default=0)),
                ('campus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reserve.campus')),
            ],
        ),
        migrations.CreateModel(
            name='Reserve',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, verbose_name='Nombre')),
                ('last_name', models.CharField(max_length=50, verbose_name='Apellido')),
                ('num_person', models.IntegerField(verbose_name='numero de personas')),
                ('telephone_number', models.CharField(max_length=20, verbose_name='Número telefónico')),
                ('email', models.EmailField(max_length=50, verbose_name='Correo')),
                ('date', models.DateField(default=datetime.date.today, verbose_name='Fecha de la reserva')),
                ('hour', models.TimeField(default='12:00', verbose_name='Hora de la reserva')),
                ('description', models.TextField(blank=True, max_length=255, null=True, verbose_name='Descripcion')),
                ('status', models.CharField(choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')], default='Activo', max_length=20, verbose_name='Estado')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha y hora de creación')),
                ('decoration', models.BooleanField(default=False, verbose_name='Decoracion')),
                ('campus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reserve.campus', verbose_name='Sede')),
            ],
        ),
    ]