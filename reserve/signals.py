from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from datetime import datetime
from pytz import timezone
from .models import Reserve


@receiver(post_save, sender=Reserve)
def set_reservation_status(sender, instance, **kwargs):
    # Definir la zona horaria de la tienda
    bogota_tz = timezone('America/Bogota')
    
    # Obtener la fecha y hora actual en la zona horaria de la tienda
    now_bogota = datetime.now(bogota_tz)

    # Verificar si la fecha y hora actual es posterior a la fecha y hora de finalización de la reserva
    if instance.date < now_bogota.date() or (instance.date == now_bogota.date() and instance.hour + timedelta(minutes=105) < now_bogota.time()):
        # Si es así, cambiar el estado de la reserva a "Inactivo"
        instance.status = 'Inactivo'
        instance.save()
"""
@receiver(pre_save, sender=Reserve)
def validate_reservation_datetime(sender, instance, **kwargs):
    # Obtener la fecha y hora actual en la zona horaria del servidor
    now = timezone.now()

    # Combinar la fecha y hora de la reserva en un objeto datetime
    reservation_datetime = timezone.make_aware(
        instance.date.combine(instance.hour),
        timezone.get_default_timezone()
    )

    # Verificar si la fecha y hora de la reserva es anterior a la fecha y hora actual
    if reservation_datetime <= now:
        raise ValueError('La fecha y hora de la reserva deben ser posteriores a la fecha y hora actuales')

"""