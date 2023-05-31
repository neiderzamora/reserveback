from rest_framework import serializers
from datetime import datetime, time, timedelta
from django.core.exceptions import ValidationError
from rest_framework.views import exception_handler
import re
from .models import Reserve

""" Horario de reservas por sede """

def generate_schedule(campus):
    if campus == "Viva":
        schedule = {
            "start_time": time(12, 0),
            "end_time": time(21, 0),
            "start_time_evening": None,
            "end_time_evening": None
        }
    elif campus == "El_Trapiche":
        schedule = {
            "start_time": time(12, 0),
            "end_time": time(15, 0),
            "start_time_evening": time(19, 0),
            "end_time_evening": time(21, 0)
        }
    else:
        schedule = None

    return schedule

""" Limitar numero de personas """

def validate_num_person(value):
    if value <= 0:
        raise ValidationError("El número de personas debe ser mayor a cero.")
    elif value > 30:
        raise ValidationError("El número de personas no debe ser mayor a 30.")
    elif not value:
        raise ValidationError("Ingrese el número de personas en la reserva.")

def validate_date(value):
    if value < datetime.now().date():
        raise ValidationError('La fecha no puede ser anterior a la actual.')
    return value

""" Validar numero """

def validate_telephone_number(value):
        pattern = r'^\d{10}$'  # Expresión regular para verificar exactamente 10 dígitos
        if not re.match(pattern, value):
            raise serializers.ValidationError("El número de teléfono debe tener exactamente 10 dígitos.")
        return value

""" Mostrar mensajes de error por json """

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code

        if isinstance(response.data, list):
            response.data = {'errors': response.data}
        else:
            response.data = {'errors': [response.data]}

    return response
