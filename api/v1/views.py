from django.db.models import Prefetch

from catalog.models import Genre, Movie, Series, Season, Episode, PublishStatus
from .serializers import (
    GenreSerializer, MovieListSerializer, MovieDetailSerializer,
    SeriesListSerializer, SeriesDetailSerializer,
)

from django.utils import timezone
from rest_framework import permissions, views, generics
from rest_framework.response import Response
from catalog.history_models import WatchProgress
from .serializers import WatchProgressSerializer

class PublishedMovieQuerysetMixin:
    """Only published movies are exposed via the public API."""
    def get_queryset(self):
        return (
            Movie.objects
            .filter(status=PublishStatus.PUBLISHED)
            .prefetch_related("genres")
        )


class PublishedSeriesQuerysetMixin:
    """Only published series, and only published episodes within them."""
    def get_queryset(self):
        published_episodes = Episode.objects.filter(status=PublishStatus.PUBLISHED)
        published_seasons = (
            Season.objects
            .filter(episodes__in=published_episodes)
            .distinct()
            .prefetch_related(Prefetch("episodes", queryset=published_episodes))
        )
        return (
            Series.objects
            .filter(status=PublishStatus.PUBLISHED)
            .prefetch_related("genres", Prefetch("seasons", queryset=published_seasons))
        )


class MovieListAPIView(PublishedMovieQuerysetMixin, generics.ListAPIView):
    serializer_class = MovieListSerializer
    lookup_field = "slug"


class MovieDetailAPIView(PublishedMovieQuerysetMixin, generics.RetrieveAPIView):
    serializer_class = MovieDetailSerializer
    lookup_field = "slug"


class SeriesListAPIView(PublishedSeriesQuerysetMixin, generics.ListAPIView):
    serializer_class = SeriesListSerializer
    lookup_field = "slug"


class SeriesDetailAPIView(PublishedSeriesQuerysetMixin, generics.RetrieveAPIView):
    serializer_class = SeriesDetailSerializer
    lookup_field = "slug"


class GenreListAPIView(generics.ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = None  # genres are few; return all


class HomeAPIView(views.APIView):
    """Convenience endpoint for the frontend landing page."""

    def get(self, request):
        latest_movies = (
            Movie.objects
            .filter(status=PublishStatus.PUBLISHED)
            .prefetch_related("genres")
            .order_by("-published_at")[:10]
        )
        latest_series = (
            Series.objects
            .filter(status=PublishStatus.PUBLISHED)
            .prefetch_related("genres")
            .order_by("-published_at")[:10]
        )
        return Response({
            "latest_movies": MovieListSerializer(latest_movies, many=True, context={"request": request}).data,
            "latest_series": SeriesListSerializer(latest_series, many=True, context={"request": request}).data,
        })


class SaveWatchProgressAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        content_type = request.data.get("content_type")
        content_id = request.data.get("content_id")
        progress_seconds = float(request.data.get("progress_seconds", 0))
        duration_seconds = float(request.data.get("duration_seconds", 0))

        if content_type == "movie":
            movie = Movie.objects.filter(pk=content_id).first()
            episode = None
        elif content_type == "episode":
            movie = None
            episode = Episode.objects.filter(pk=content_id).first()
        else:
            return Response({"detail": "Invalid content type."}, status=400)

        if not (movie or episode):
            return Response({"detail": "Content not found."}, status=404)

        # If watched more than 95%, consider it finished and remove it from history
        if duration_seconds > 0 and (progress_seconds / duration_seconds) > 0.95:
            WatchProgress.objects.filter(user=request.user, movie=movie, episode=episode).delete()
            return Response({"status": "finished"})

        # Update or create the progress record
        progress, created = WatchProgress.objects.update_or_create(
            user=request.user,
            movie=movie,
            episode=episode,
            defaults={
                "progress_seconds": progress_seconds,
                "duration_seconds": duration_seconds,
            }
        )
        return Response(WatchProgressSerializer(progress).data)


class WatchHistoryAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Only return the last 10 items to keep the home page clean
        history = WatchProgress.objects.filter(user=request.user).select_related(
            "movie", "episode", "episode__season", "episode__season__series"
        ).order_by("-updated_at")[:10]
        
        return Response(WatchProgressSerializer(history, many=True).data)


from accounts.profile_models import Profile

class SaveWatchProgressAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        profile_id = request.data.get("profile_id")
        if not profile_id:
            return Response({"detail": "profile_id is required."}, status=400)
        profile = Profile.objects.filter(id=profile_id, user=request.user).first()
        if not profile:
            return Response({"detail": "Profile not found."}, status=404)

        content_type = request.data.get("content_type")
        content_id = request.data.get("content_id")
        progress_seconds = float(request.data.get("progress_seconds", 0))
        duration_seconds = float(request.data.get("duration_seconds", 0))

        if content_type == "movie":
            movie, episode = Movie.objects.filter(pk=content_id).first(), None
        elif content_type == "episode":
            movie, episode = None, Episode.objects.filter(pk=content_id).first()
        else:
            return Response({"detail": "Invalid content type."}, status=400)

        if not (movie or episode):
            return Response({"detail": "Content not found."}, status=404)

        if duration_seconds > 0 and (progress_seconds / duration_seconds) > 0.95:
            WatchProgress.objects.filter(profile=profile, movie=movie, episode=episode).delete()
            return Response({"status": "finished"})

        WatchProgress.objects.update_or_create(
            profile=profile, movie=movie, episode=episode,
            defaults={"progress_seconds": progress_seconds, "duration_seconds": duration_seconds},
        )
        return Response({"status": "ok"})

class WatchHistoryAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile_id = request.query_params.get("profile_id")
        if not profile_id:
            return Response([])
        profile = Profile.objects.filter(id=profile_id, user=request.user).first()
        if not profile:
            return Response([], status=404)

        history = WatchProgress.objects.filter(profile=profile).select_related(
            "movie", "episode", "episode__season", "episode__season__series"
        ).order_by("-updated_at")[:10]
        return Response(WatchProgressSerializer(history, many=True).data)
