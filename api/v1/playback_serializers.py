from rest_framework import serializers


class PlaybackTokenSerializer(serializers.Serializer):
    """Output shape for playback endpoints. Will gain stream_url in Task 12."""
    token = serializers.CharField()
    content_type = serializers.CharField()
    content_id = serializers.IntegerField()
    expires_in_seconds = serializers.IntegerField()
