from rest_framework import serializers
from .utils import *
from .models import *
from datetime import datetime, time, timedelta
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
import pytz

class ReserveSerializer(serializers.ModelSerializer):
    campus = serializers.SlugRelatedField(slug_field='name', queryset=Campus.objects.all())
    #time_slot = serializers.SlugRelatedField(slug_field='start_time', validators=[slot])
    hour = serializers.TimeField(format="%H:%M", input_formats=["%H:%M"])
    num_person = serializers.IntegerField(validators=[validate_num_person])
    date = serializers.DateField(validators=[validate_date])
    telephone_number = serializers.CharField(validators=[validate_telephone_number])
    created_at = serializers.DateTimeField(format='%Y-%m-%e %H:%M', read_only=True)


    name = serializers.CharField(error_messages={
        'blank': 'Por favor, Ingrese su nombre.',
        'invalid': 'Nombre no registrado.',
        'required': 'El nombre es obligatorio.'
    })
    last_name = serializers.CharField(error_messages={
        'blank': 'Por favor, Ingrese su apellido.',
        'invalid': 'Apellido no registrado.'
    })
    email = serializers.EmailField(error_messages={
        'blank': 'Por favor, Ingrese su correo electronico.',
        'invalid': 'Correo electronico no registrado.'
    })

    def validate_hour(self, value):
        campus = self.initial_data.get('campus')
        schedule = generate_schedule(campus)

        if not schedule:
            raise serializers.ValidationError("Sede no válida.")

        start_time = schedule.get('start_time')
        end_time = schedule.get('end_time')
        start_time_evening = schedule.get('start_time_evening')
        end_time_evening = schedule.get('end_time_evening')

        if start_time and end_time and start_time_evening and end_time_evening:
            if not ((start_time <= value <= end_time) or (start_time_evening <= value <= end_time_evening)):
                error_msg = f"La hora no está dentro del horario permitido ({start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}) o ({start_time_evening.strftime('%H:%M')} - {end_time_evening.strftime('%H:%M')})."
                raise serializers.ValidationError(error_msg)
        elif start_time and end_time:
            if not (start_time <= value <= end_time):
                error_msg = f"La hora no está dentro del horario permitido ({start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')})."
                raise serializers.ValidationError(error_msg)
        elif start_time_evening and end_time_evening:
            if not (start_time_evening <= value <= end_time_evening):
                error_msg = f"La hora no está dentro del horario permitido ({start_time_evening.strftime('%H:%M')} - {end_time_evening.strftime('%H:%M')})."
                raise serializers.ValidationError(error_msg)

        return value
    
    def validate(self, data):

        start_datetime = datetime.combine(data['date'], data['hour'])
        end_datetime = start_datetime + timedelta(minutes=105)

        conflicting_slot = TimeSlot.objects.filter(
            campus=data['campus'],
            start_time__lt=end_datetime,
            start_time__gt=start_datetime - timedelta(minutes=105),
            current_capacity__gte=F('max_capacity') - data['num_person'],
        ).first()

        if conflicting_slot:
            bogota_tz = pytz.timezone('America/Bogota')
            end_time_bogota = conflicting_slot.start_time.astimezone(bogota_tz) + conflicting_slot.duration
            end_time_str = end_time_bogota.strftime("%I:%M %p")
            raise serializers.ValidationError(
                f"No hay suficiente capacidad disponible para esta reserva. La disponibilidad más pronta es: {end_time_str}. Por favor considere la opción de anticipar o postergar la hora."
            )

        return data

    class Meta:
        model = Reserve
        fields = ['id', 'name', 'last_name', 'num_person', 'telephone_number', 'campus', 'email', 'date', 'hour', 'description', 'status', 'created_at', 'decoration', 'time_slot']
        read_only_fields = ['id', 'created_at']

