from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from .models import CustomUser
from rest_framework.response import Response

def send_email(subject, message, recipient_list, from_email=None):
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL  

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False
    )

def notify_admin(notification_type,details,user_email):
    subject = f"new {notification_type}: {details.get('title')}"
    message =( 
        f"new {notification_type} \n \n" 
        f"Details:\n"
        )

    for key,value in details.items():
        message += f"{key.capitalize()}: {value}\n"
    
    admin_email = settings.DEFAULT_FROM_EMAIL
    send_email(subject,message,[admin_email],from_email=user_email)

def notify_user(notification_type,details,user_email):
    subject = f"new {notification_type} confirmation"
    message = (
        f" thank you for your {notification_type.lower()}.\n\n"
        f"Details:\n"
    )
    
    for key,value in details.items():
        message += f"{key.capitalize()}: {value}\n"

    send_email(subject,message,[user_email])



