from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ContactQuery
from django.conf import settings
from .utils import notify_admin

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
       