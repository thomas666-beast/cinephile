from django.shortcuts import get_object_or_404
from rest_framework import status, views
from rest_framework.response import Response

from catalog.models import Movie, Episode, PublishStatus
from subscriptions.access import has_active_subscription
from subscriptions.permissions import IsSubscriber
from subscriptions.playback import issue_playback_token, PLAYBACK_TOKEN_LIFETIME
from .playback_serializers import PlaybackTokenSerializer


class MoviePlaybackAPIView(views.APIView):
    permission_classes = [IsSubscriber]

    def post(self, request, slug):
        movie = get_object_or_404(
            Movie, slug=slug, status=PublishStatus.PUBLISHED
        )
        token = issue_playback_token(
            user=request.user, content_type="movie", content_id=movie.id,
        )
        return Response(PlaybackTokenSerializer({
            "token": token,
            "content_type": "movie",
            "content_id": movie.id,
            "expires_in_seconds": int(PLAYBACK_TOKEN_LIFETIME.total_seconds()),
        }).data, status=status.HTTP_200_OK)


class EpisodePlaybackAPIView(views.APIView):
    permission_classes = [IsSubscriber]

    def post(self, request, pk):
        episode = get_object_or_404(
            Episode,
            pk=pk,
            status=PublishStatus.PUBLISHED,
            season__series__status=PublishStatus.PUBLISHED,
        )
        token = issue_playback_token(
            user=request.user, content_type="episode", content_id=episode.id,
        )
        return Response(PlaybackTokenSerializer({
            "token": token,
            "content_type": "episode",
            "content_id": episode.id,
            "expires_in_seconds": int(PLAYBACK_TOKEN_LIFETIME.total_seconds()),
        }).data, status=status.HTTP_200_OK)
