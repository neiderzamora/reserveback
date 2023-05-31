from django.db import models
from .models import *
from django.core.exceptions import ObjectDoesNotExist
import uuid
from datetime import date, datetime, time, timedelta
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.utils import timezone
from django.db.models import F
import pytz
from django.db.models import Sum


class Campus(models.Model):
    CAMPUS_CHOICES = (
        ('Viva', 'Viva'),
        ('El_Trapiche', 'El Trapiche'),
    )
    name = models.CharField(max_length=50, choices=CAMPUS_CHOICES, unique=True)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class TimeSlot(models.Model):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    duration = models.DurationField()
    max_capacity = models.IntegerField(default=30)
    current_capacity = models.IntegerField(default=0)

    def update_current_capacity(self):
        self.current_capacity = self.reserve_set.aggregate(Sum('num_person'))['num_person__sum'] or 0
        self.save(update_fields=['current_capacity'])

    def __str__(self):
        return f'{self.campus.name} - {self.start_time} - {self.current_capacity}'


class Reserve(models.Model):
    STATUS_CHOICES = (
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        verbose_name='Nombre'
    )
    last_name = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        verbose_name='Apellido'
    )
    num_person = models.IntegerField(
        blank=False,
        null=False,
        verbose_name='Número de personas'
    )
    telephone_number = models.CharField(
        max_length=20,
        blank=False,
        null=False,
        verbose_name='Número telefónico'
    )
    campus = models.ForeignKey(
        Campus,
        on_delete=models.CASCADE,
        verbose_name='Sede'
    )
    email = models.EmailField(
        max_length=50,
        blank=False,
        null=False,
        verbose_name='Correo'
    )
    date = models.DateField(
        verbose_name='Fecha de la reserva',
        default=date.today,
        blank=False,
        null=False
    )
    hour = models.TimeField(
        verbose_name='Hora de la reserva',
        default='12:00',
        blank=False,
        null=False
    )
    description = models.TextField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Activo',
        verbose_name='Estado'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name='Fecha y hora de creación'
    )
    decoration = models.BooleanField(
        default=False,
        verbose_name='Decoración'
    )
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        is_new_reserve = self.pk is None  # Verificar si es una reserva nueva o una edición

        # Restablecer la capacidad anterior del time_slot si la reserva ya existe
        previous_reserve = None
        if not is_new_reserve:
            try:
                previous_reserve = Reserve.objects.get(pk=self.pk)
            except Reserve.DoesNotExist:
                pass

        if previous_reserve and previous_reserve.time_slot:
            previous_time_slot = previous_reserve.time_slot
            previous_time_slot.current_capacity -= previous_reserve.num_person
            previous_time_slot.save()

        # Actualizar la capacidad del time_slot para la nueva reserva o la reserva actualizada
        if self.time_slot:
            if is_new_reserve:
                self.time_slot.current_capacity += self.num_person
            else:
                if self.num_person != previous_reserve.num_person:
                    self.time_slot.current_capacity -= previous_reserve.num_person
                    self.time_slot.current_capacity += self.num_person
            self.time_slot.current_capacity = max(0, self.time_slot.current_capacity)  # Asegurar que no sea negativo
            self.time_slot.save()

        # Restablecer el time_slot de la reserva anterior si se actualiza el time_slot
        if previous_reserve and self.time_slot != previous_reserve.time_slot:
            previous_reserve.time_slot = None
            previous_reserve.save()

        # Definir el horario de la reserva
        opening_time = datetime.combine(self.date, datetime.min.time()) + timedelta(hours=12)
        closing_time = datetime.combine(self.date, datetime.min.time()) + timedelta(hours=21)

        # Definir el intervalo de tiempo de la reserva
        start_datetime = datetime.combine(self.date, self.hour)
        end_datetime = start_datetime + timedelta(minutes=105)

        # Verificar si la reserva está dentro del horario de la tienda
        if not (opening_time <= start_datetime < closing_time):
            error_msg = "Lo sentimos. La reserva está fuera del horario establecido."
            raise serializers.ValidationError(error_msg)

        # Verificar si existe algún TimeSlot que se superponga con la nueva reserva y exceda la capacidad máxima
        conflicting_slot = TimeSlot.objects.filter(
            campus=self.campus,
            start_time__lt=end_datetime,
            start_time__gt=start_datetime - timedelta(minutes=105),
            current_capacity__gte=F('max_capacity') - self.num_person,
        ).first()

        if conflicting_slot:
            bogota_tz = pytz.timezone('America/Bogota')
            end_time_bogota = conflicting_slot.start_time.astimezone(bogota_tz) + conflicting_slot.duration
            end_time_str = end_time_bogota.strftime("%I:%M %p")
            error_msg = f"No hay suficiente capacidad disponible para esta reserva. La disponibilidad más pronta es: {end_time_str}. Por favor considere la opción de anticipar o postergar la hora."
            raise serializers.ValidationError(error_msg)

        # Buscar o crear el intervalo de tiempo correspondiente a esta reserva
        time_slot = TimeSlot.objects.filter(
            campus=self.campus,
            start_time__lte=start_datetime,
            start_time__gt=start_datetime - timedelta(minutes=105),
        ).first()

        if time_slot is None:
            # Si no se encuentra un intervalo de tiempo, crear uno nuevo
            time_slot = TimeSlot(
                campus=self.campus,
                start_time=start_datetime,
                duration=timedelta(minutes=105),
                max_capacity=30,
                current_capacity=self.num_person,
            )
            time_slot.save()
        else:
            # Agregar la cantidad de personas a un time_slot existente
            time_slot.current_capacity += self.num_person

        time_slot.save()

        self.time_slot = time_slot
        super(Reserve, self).save(*args, **kwargs)

        # Actualizar el current_capacity del TimeSlot después de guardar la reserva
        if self.time_slot:
            self.time_slot.update_current_capacity()

    def delete(self, *args, **kwargs):
        if self.time_slot:
            self.time_slot.current_capacity -= self.num_person
            self.time_slot.current_capacity = max(0, self.time_slot.current_capacity)  # Asegurar que no sea negativo
            self.time_slot.save()

        super(Reserve, self).delete(*args, **kwargs)

