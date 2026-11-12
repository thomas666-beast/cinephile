from django.db.models import Prefetch
from rest_framework import generics, views
from rest_framework.response import Response

from catalog.models import Genre, Movie, Series, Season, PublishStatus
from .serializers import (
    GenreSerializer, MovieListSerializer, MovieDetailSerializer,
    SeriesListSerializer, SeriesDetailSerializer,
)


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
