from rest_framework import generics, permissions, parsers, status
from rest_framework.response import Response

from catalog.models import VideoAsset
from catalog.serializers import VideoAssetSerializer


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
