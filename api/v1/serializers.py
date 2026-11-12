from rest_framework import serializers
from catalog.models import Genre, Movie, Series, Season, Episode


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name", "slug")


class MovieListSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = (
            "id", "title", "slug", "release_year",
            "duration_minutes", "poster", "genres", "published_at",
        )


class MovieDetailSerializer(MovieListSerializer):
    class Meta(MovieListSerializer.Meta):
        fields = MovieListSerializer.Meta.fields + (
            "synopsis", "backdrop", "created_at", "updated_at",
        )


class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = (
            "id", "number", "title", "synopsis",
            "duration_minutes", "still", "air_date",
        )


class SeasonSerializer(serializers.ModelSerializer):
    episodes = EpisodeSerializer(many=True, read_only=True)

    class Meta:
        model = Season
        fields = ("id", "number", "title", "synopsis", "poster", "episodes")


class SeriesListSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Series
        fields = (
            "id", "title", "slug", "start_year", "end_year",
            "poster", "genres", "published_at",
        )


class SeriesDetailSerializer(SeriesListSerializer):
    seasons = SeasonSerializer(many=True, read_only=True)

    class Meta(SeriesListSerializer.Meta):
        fields = SeriesListSerializer.Meta.fields + (
            "synopsis", "backdrop", "seasons", "created_at", "updated_at",
        )
