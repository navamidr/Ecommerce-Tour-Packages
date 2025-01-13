from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from .models import ContactQuery
from django.conf import settings
from django.core.mail import send_mail


@receiver(post_save,sender=ContactQuery)
def send_contact_email_to_admim(sender,instance,created,**kwargs):
    if created:
        subject = f"New Contact Query from {instance.name}"
        admin_message = (
            f"You have received a new query/feedback from {instance.name}.\n\n"
            f"Details:\n"
            f"Name: {instance.name}\n"
            f"Email: {instance.email}\n"
            f"Contact Number: {instance.contact}\n"
            f"Message:\n{instance.messages}\n\n"
            f"Submitted on: {instance.created_date}"
        )
        admin_email = settings.DEFAULT_FROM_EMAIL

        send_mail(
            subject,
            admin_message,
            instance.email,  
            [admin_email],    
            fail_silently=False
        )
