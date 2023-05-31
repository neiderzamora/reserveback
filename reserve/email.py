from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.utils.html import format_html

def is_valid_reservation(date, hour, campus, num_person):
    # Implementa la validación de la reserva aquí
    pass

def validate_num_person(num_person):
    # Implementa la validación del número de personas aquí
    pass

def validate_telefone_number(telefone_number):
    # Implementa la validación del número de teléfono aquí
    pass

def send_confirmation_email(name, last_name, email, date, hour):
    subject = 'Confirmación de reserva'
    message_text = f'Hola {name} {last_name}, \n\nGracias por reservar con nosotros. Tu reserva ha sido confirmada.\n\nFecha {date} Hora {hour}.\n\n¡Esperamos verte pronto!'

    message_html = format_html('''
        <html><head><style>.container {{font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;max-width: 600px;margin: 0 auto;padding: 20px;background-color: #f7fcff;backdrop-filter: blur(8px);}}h1 {{font-size: 32px;font-weight: bold;color: #d64541;margin-bottom: 30px;text-align: center;}}p {{font-size: 18px;color: #333333;line-height: 1.5;margin-bottom: 20px;}}.highlight {{background-color: #f9a825;color: #ffffff;padding: 10px 20px;border-radius: 6px;}}.logo {{display: block;margin: 0 auto;max-width: 100px;border:6px solid #d64541;border-radius: 50%;box-shadow: 0 0 20px rgba(214, 69, 65, 0.6);}}</style></head><body><div class="container"><table style="width:100%"><tr><td style="text-align:center;"><img src="https://cdn.discordapp.com/attachments/830232986392985622/1112055409138733166/limoncello_logo_IA.png" alt="Logo" class="logo"></td></tr></table><h1>Confirmación de reserva</h1><p>Hola {name} {last_name},</p><p>Gracias por reservar con nosotros. Tu reserva ha sido confirmada para la fecha {date} y hora {hour}.</p><p class="highlight">¡Esperamos verte pronto y te recordamos la importancia de la puntualidad⏰ para brindarte el mejor servicio posible! 🍝🍷</p></div></body></html>
    ''', name=name, last_name=last_name, date=date, hour=hour)

    email = EmailMultiAlternatives(subject, message_text, 'reservas@limoncello.com.co', [email])
    email.attach_alternative(message_html, "text/html")
    email.send()