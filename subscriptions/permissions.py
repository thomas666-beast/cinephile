from rest_framework import permissions
from .access import has_active_subscription


class IsSubscriber(permissions.BasePermission):
    """Grants access only to users with an active subscription (or admins)."""
    message = "An active subscription is required to access this content."

    def has_permission(self, request, view):
        return has_active_subscription(request.user)
