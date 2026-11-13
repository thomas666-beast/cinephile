import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if not created:
        return
    if not instance.email:
        return
    try:
        send_mail(
            subject="Welcome to Cinephile",
            message=(
                f"Hi{(' ' + instance.first_name) if instance.first_name else ''},\n\n"
                "Welcome to Cinephile. Your account is ready.\n\n"
                "You can now sign in and subscribe to start watching.\n\n"
                "— Cinephile"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=True,
        )
    except Exception:
        logger.exception("Failed to send welcome email to %s", instance.email)
