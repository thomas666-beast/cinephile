from rest_framework import serializers
from .models import VideoAsset


class VideoAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoAsset
        fields = (
            "id", "movie", "episode", "video_file", "mime_type",
            "original_filename", "file_size_bytes", "status",
            "hls_manifest_path", "created_at",
        )
        read_only_fields = (
            "id", "original_filename", "file_size_bytes", "status",
            "hls_manifest_path", "created_at",
        )

    def validate(self, attrs):
        movie = attrs.get("movie") or getattr(self.instance, "movie", None)
        episode = attrs.get("episode") or getattr(self.instance, "episode", None)
        if (movie is None) == (episode is None):
            raise serializers.ValidationError(
                "Provide exactly one of `movie` or `episode`."
            )
        return attrs
