from django.utils import timezone
from .models import Subscription


def has_active_subscription(user) -> bool:
    """
    Single source of truth for 'can this user watch content right now?'
    Every playback gate should call this, not query Subscription directly.
    """
    if not user or not user.is_authenticated:
        return False
    if user.is_staff or user.role == "admin":
        # Admins always have access — they need it to test content.
        return True
    return Subscription.objects.filter(
        user=user,
        status=Subscription.Status.ACTIVE,
        expires_at__gt=timezone.now(),
    ).exists()


def get_active_subscription(user):
    """Return the user's active subscription, or None. Also expires stale ones."""
    if not user or not user.is_authenticated:
        return None

    now = timezone.now()
    # Lazily expire any subscriptions whose time has passed
    Subscription.objects.filter(
        user=user, status=Subscription.Status.ACTIVE, expires_at__lte=now
    ).update(status=Subscription.Status.EXPIRED)

    return Subscription.objects.filter(
        user=user, status=Subscription.Status.ACTIVE, expires_at__gt=now
    ).select_related("plan").first()
