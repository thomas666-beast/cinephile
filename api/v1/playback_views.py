from urllib.parse import urlencode

from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import status, views
from rest_framework.response import Response

from catalog.models import Movie, Episode, VideoAsset, PublishStatus
from subscriptions.permissions import IsSubscriber
from subscriptions.playback import issue_playback_token, PLAYBACK_TOKEN_LIFETIME
from .playback_serializers import PlaybackResponseSerializer


def _latest_ready_asset(movie=None, episode=None) -> VideoAsset | None:
    qs = VideoAsset.objects.filter(status=VideoAsset.Status.READY)
    if movie is not None:
        qs = qs.filter(movie=movie)
    else:
        qs = qs.filter(episode=episode)
    return qs.order_by("-created_at").first()


def _build_playback_payload(
    *,
    request,
    token,
    content_type,
    content_id,
    content_ident,
    asset,
):
    """
    Build the response body. If the asset isn't ready yet, return manifest URL=None
    so the frontend can render a 'still processing' state instead of an error.

    `content_ident` is what the stream route expects:
      - movie: the slug (str)
      - episode: the pk (int)
    """
    manifest_url = None
    renditions = []
    duration = None

    if asset and asset.status == VideoAsset.Status.READY:
        stream_route = (
            "v1:playback-stream-movie-master"
            if content_type == "movie"
            else "v1:playback-stream-episode-master"
        )
        path = reverse(stream_route, kwargs={"ident": content_ident})
        manifest_url = f"{path}?{urlencode({'token': token})}"
        renditions = asset.available_renditions()

    data = {
        "token": token,
        "content_type": content_type,
        "content_id": content_id,
        "expires_in_seconds": int(PLAYBACK_TOKEN_LIFETIME.total_seconds()),
        "hls_manifest_url": manifest_url,
        "duration_seconds": duration,
        "renditions": renditions,
    }
    return PlaybackResponseSerializer(data).data


class MoviePlaybackAPIView(views.APIView):
    permission_classes = [IsSubscriber]

    def post(self, request, slug):
        movie = get_object_or_404(Movie, slug=slug, status=PublishStatus.PUBLISHED)
        asset = _latest_ready_asset(movie=movie)
        if asset is None:
            return Response(
                {"detail": "This movie is not yet available for streaming."},
                status=status.HTTP_409_CONFLICT,
            )
        token = issue_playback_token(
            user=request.user, content_type="movie", content_id=movie.id,
        )
        payload = _build_playback_payload(
            request=request,
            token=token,
            content_type="movie",
            content_id=movie.id,
            content_ident=movie.slug,
            asset=asset,
        )
        return Response(payload, status=status.HTTP_200_OK)


class EpisodePlaybackAPIView(views.APIView):
    permission_classes = [IsSubscriber]

    def post(self, request, pk):
        episode = get_object_or_404(
            Episode,
            pk=pk,
            status=PublishStatus.PUBLISHED,
            season__series__status=PublishStatus.PUBLISHED,
        )
        asset = _latest_ready_asset(episode=episode)
        if asset is None:
            return Response(
                {"detail": "This episode is not yet available for streaming."},
                status=status.HTTP_409_CONFLICT,
            )
        token = issue_playback_token(
            user=request.user, content_type="episode", content_id=episode.id,
        )
        payload = _build_playback_payload(
            request=request,
            token=token,
            content_type="episode",
            content_id=episode.id,
            content_ident=episode.id,
            asset=asset,
        )
        return Response(payload, status=status.HTTP_200_OK)
