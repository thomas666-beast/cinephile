from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from accounts.profile_models import Profile
from .profile_serializers import ProfileSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user).order_by("created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if Profile.objects.filter(user=request.user).count() <= 1:
            return Response(
                {"detail": "You must keep at least one profile."},
                status=status.HTTP_409_CONFLICT,
            )
        return super().destroy(request, *args, **kwargs)
