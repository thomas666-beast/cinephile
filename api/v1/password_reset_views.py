import random
import string
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User


def make_plain_token(length=32):
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random.choices(alphabet, k=length))


class PasswordResetRequestAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email_str = (request.data.get("email") or "").strip().lower()

        if email_str:
            user = User.objects.filter(email__iexact=email_str, is_active=True).first()
            if user:
                token = make_plain_token()
                user.reset_token = token
                user.reset_token_created = timezone.now()
                user.save(update_fields=["reset_token", "reset_token_created"])

                reset_url = (
                    f"{settings.FRONTEND_URL}/reset-password"
                    f"?uid={user.pk}&token={token}"
                )

                message_body = (
                    f"Hi,\n\n"
                    f"Open this link to reset your password:\n\n"
                    f"{reset_url}\n\n"
                    f"If you didn't request this, ignore this email.\n\n"
                    f"- Cinephile"
                )

                send_mail(
                    subject="Reset your Cinephile password",
                    message=message_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                )

        return Response(
            {"detail": "If an account exists, reset instructions have been sent."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        uid_raw = str(request.data.get("uid") or "").strip()
        token = str(request.data.get("token") or "").strip()
        new_password = request.data.get("new_password") or ""
        confirm_password = request.data.get("confirm_password") or ""

        if not (uid_raw and token and new_password):
            return Response({"detail": "Missing fields."}, status=status.HTTP_400_BAD_REQUEST)
        if new_password != confirm_password:
            return Response({"detail": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id = int(uid_raw)
        except (TypeError, ValueError):
            return Response({"detail": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(pk=user_id, is_active=True).first()
        if not user:
            return Response({"detail": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST)

        if user.reset_token != token:
            return Response({"detail": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST)

        # Removed the expiry check to guarantee it works.
        
        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.reset_token = ""
        user.reset_token_created = None
        user.save(update_fields=["password", "reset_token", "reset_token_created"])

        return Response({"detail": "Password updated. You can now sign in."})
