from rest_framework import serializers


class PlaybackResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    content_type = serializers.CharField()
    content_id = serializers.IntegerField()
    expires_in_seconds = serializers.IntegerField()
    # New in Task 12:
    hls_manifest_url = serializers.CharField(allow_null=True)
    duration_seconds = serializers.FloatField(allow_null=True)
    renditions = serializers.ListField(child=serializers.CharField(), allow_empty=True)
