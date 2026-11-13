from django.contrib.auth import get_user_model
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken, OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

from .auth_serializers import RegisterSerializer, UserProfileSerializer

from rest_framework import generics, permissions, parsers, status
from rest_framework.response import Response

from catalog.models import VideoAsset
from catalog.serializers import VideoAssetSerializer

User = get_user_model()


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LogoutAPIView(generics.GenericAPIView):
    """Blacklists the provided refresh token. Access token stays valid until expiry."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"detail": "Invalid or already-blacklisted token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_205_RESET_CONTENT)


class MeAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        return self.request.user


class IsStaff(permissions.BasePermission):
    message = "Admin access required."
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class VideoUploadAPIView(generics.CreateAPIView):
    """Multipart upload. For programmatic clients (e.g., the Vue admin panel)."""
    permission_classes = [IsStaff]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    serializer_class = VideoAssetSerializer


class CompleteVideoUploadAPIView(generics.GenericAPIView):
    """Mark a VideoAsset as ready for transcoding (used when the client wants to
    decouple 'file uploaded' from 'we're ready to process')."""
    permission_classes = [IsStaff]

    def post(self, request, pk):
        asset = VideoAsset.objects.filter(pk=pk).first()
        if not asset:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        if asset.status != VideoAsset.Status.UPLOADED:
            return Response(
                {"detail": f"Cannot complete: asset is {asset.status}."},
                status=status.HTTP_409_CONFLICT,
            )
        # No-op for local storage (file is already saved); hook point for Task 11.
        return Response({"id": asset.id, "status": asset.status})