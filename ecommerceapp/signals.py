from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ContactQuery
from django.conf import settings
from .utils import notify_admin
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=ContactQuery)
def send_contact_email_to_admin(sender, instance, created, **kwargs):
    if created:
        details = {
            
            "name":instance.name,
            "email":instance.email,
            "contact":instance.contact,
            "message":instance.messages,
            "submitted_on":instance.created_date.strftime("%Y-%m-%d %H:%M:%S"),
        }

        notify_admin(
            notification_type="contact Query",
            details=details,
            user_email=instance.email
        )
       # Notify the User
        subject = "We Received Your Contact Query"
        message = (
            f"Hi {instance.name},\n\n"
            f"Thank you for your Contact Query.\n\n"
            f"Best regards,\nThe Support Team"
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # Use your project's default sender email
            [instance.email],  # Recipient email
            fail_silently=False,  # Raise an error if email sending fails
        )