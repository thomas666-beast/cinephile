from rest_framework import serializers
from catalog.models import Genre, Movie, Series, Season, Episode
from catalog.history_models import WatchProgress


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

class WatchProgressSerializer(serializers.ModelSerializer):
    content_type = serializers.SerializerMethodField()
    content_id = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    poster = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    percent = serializers.FloatField(source="percent_complete", read_only=True)

    class Meta:
        model = WatchProgress
        fields = (
            "id", "content_type", "content_id", "title", "poster", "slug", 
            "progress_seconds", "duration_seconds", "percent", "updated_at"
        )

    def get_content_type(self, obj):
        return "movie" if obj.movie_id else "episode"

    def get_content_id(self, obj):
        return obj.movie_id or obj.episode_id

    def get_title(self, obj):
        if obj.movie:
            return obj.movie.title
        return f"S{obj.episode.season.number:02d}E{obj.episode.number:02d} — {obj.episode.title}"

    def get_poster(self, obj):
        if obj.movie:
            return obj.movie.poster.url if obj.movie.poster else None
        if obj.episode.season.series.poster:
            return obj.episode.season.series.poster.url
        return None

    def get_slug(self, obj):
        if obj.movie:
            return obj.movie.slug
        return obj.episode.season.series.slug
