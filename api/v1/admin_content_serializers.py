from rest_framework import serializers
from catalog.models import Genre, Movie, Series, Season, Episode, VideoAsset


class AdminGenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name", "slug")
        read_only_fields = ("slug",)


class AdminMovieSerializer(serializers.ModelSerializer):
    genres = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), many=True, required=False
    )
    genre_names = serializers.SerializerMethodField(read_only=True)
    video_status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Movie
        fields = (
            "id", "title", "slug", "synopsis", "release_year",
            "duration_minutes", "genres", "genre_names",
            "poster", "backdrop", "status", "published_at",
            "video_status", "created_at", "updated_at",
        )
        read_only_fields = ("slug", "published_at", "created_at", "updated_at")

    def get_genre_names(self, obj):
        return [g.name for g in obj.genres.all()]

    def get_video_status(self, obj):
        latest = obj.videos.order_by("-created_at").first()
        if not latest:
            return None
        return {
            "id": latest.id,
            "status": latest.status,
            "processing_error": latest.processing_error or None,
            "hls_manifest_path": latest.hls_manifest_path or None,
        }


class AdminEpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = (
            "id", "season", "number", "title", "synopsis",
            "duration_minutes", "air_date", "still", "status",
        )


class AdminSeasonSerializer(serializers.ModelSerializer):
    series = serializers.SlugRelatedField(slug_field="slug", queryset=Series.objects.all())
    episodes = AdminEpisodeSerializer(many=True, read_only=True)

    class Meta:
        model = Season
        fields = ("id", "series", "number", "title", "synopsis", "poster", "episodes")


class AdminSeriesSerializer(serializers.ModelSerializer):
    genres = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), many=True, required=False
    )
    genre_names = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Series
        fields = (
            "id", "title", "slug", "synopsis", "start_year", "end_year",
            "genres", "genre_names", "poster", "backdrop",
            "status", "published_at", "created_at", "updated_at",
        )
        read_only_fields = ("slug", "published_at", "created_at", "updated_at")

    def get_genre_names(self, obj):
        return [g.name for g in obj.genres.all()]
