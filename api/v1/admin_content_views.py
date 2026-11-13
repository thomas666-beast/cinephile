from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from catalog.models import Genre, Movie, Series, Season, Episode, PublishStatus
from .admin_content_serializers import (
    AdminGenreSerializer, AdminMovieSerializer, AdminSeriesSerializer,
    AdminSeasonSerializer, AdminEpisodeSerializer,
)


class IsStaff(permissions.BasePermission):
    message = "Admin access required."
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class AdminGenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all().order_by("name")
    serializer_class = AdminGenreSerializer
    permission_classes = [IsStaff]
    pagination_class = None


class AdminMovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all().prefetch_related("genres")
    serializer_class = AdminMovieSerializer
    permission_classes = [IsStaff]
    lookup_field = "slug"
    filterset_fields = ("status",)
    search_fields = ("title", "synopsis")

    @action(detail=True, methods=["post"])
    def publish(self, request, slug=None):
        movie = self.get_object()
        movie.status = PublishStatus.PUBLISHED
        movie.save()
        return Response(self.get_serializer(movie).data)

    @action(detail=True, methods=["post"])
    def unpublish(self, request, slug=None):
        movie = self.get_object()
        movie.status = PublishStatus.DRAFT
        movie.save()
        return Response(self.get_serializer(movie).data)


class AdminSeriesViewSet(viewsets.ModelViewSet):
    queryset = Series.objects.all().prefetch_related("genres", "seasons__episodes")
    serializer_class = AdminSeriesSerializer
    permission_classes = [IsStaff]
    lookup_field = "slug"
    filterset_fields = ("status",)
    search_fields = ("title",)

    @action(detail=True, methods=["post"])
    def publish(self, request, slug=None):
        s = self.get_object()
        s.status = PublishStatus.PUBLISHED
        s.save()
        return Response(self.get_serializer(s).data)

    @action(detail=True, methods=["post"])
    def unpublish(self, request, slug=None):
        s = self.get_object()
        s.status = PublishStatus.DRAFT
        s.save()
        return Response(self.get_serializer(s).data)


class AdminSeasonViewSet(viewsets.ModelViewSet):
    queryset = Season.objects.all()
    serializer_class = AdminSeasonSerializer
    permission_classes = [IsStaff]


class AdminEpisodeViewSet(viewsets.ModelViewSet):
    queryset = Episode.objects.all()
    serializer_class = AdminEpisodeSerializer
    permission_classes = [IsStaff]


# ---------- Dashboard stats ----------

from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from subscriptions.models import Subscription
from catalog.models import VideoAsset

User = get_user_model()


class AdminStatsAPIView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        return Response({
            "movies": {
                "total": Movie.objects.count(),
                "published": Movie.objects.filter(status=PublishStatus.PUBLISHED).count(),
                "draft": Movie.objects.filter(status=PublishStatus.DRAFT).count(),
            },
            "series": {
                "total": Series.objects.count(),
                "published": Series.objects.filter(status=PublishStatus.PUBLISHED).count(),
                "draft": Series.objects.filter(status=PublishStatus.DRAFT).count(),
            },
            "videos": {
                "ready": VideoAsset.objects.filter(status=VideoAsset.Status.READY).count(),
                "processing": VideoAsset.objects.filter(status=VideoAsset.Status.PROCESSING).count(),
                "failed": VideoAsset.objects.filter(status=VideoAsset.Status.FAILED).count(),
            },
            "users": {
                "total": User.objects.count(),
                "staff": User.objects.filter(is_staff=True).count(),
            },
            "subscriptions": {
                "active": Subscription.objects.filter(status=Subscription.Status.ACTIVE).count(),
            },
        })
