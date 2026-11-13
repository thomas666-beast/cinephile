import re
from pathlib import Path
from urllib.parse import urlencode

import jwt
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from catalog.models import Movie, Episode, VideoAsset, PublishStatus
from subscriptions.playback import verify_playback_token


RENDITION_RE = re.compile(r"^[a-z0-9]{2,8}$")               # 360p, 720p, 1080p
FILE_RE = re.compile(r"^[a-zA-Z0-9_.-]+\.(m3u8|ts|mp4)$")    # seg_000.ts, index.m3u8

MIME_BY_EXT = {
    ".m3u8": "application/vnd.apple.mpegurl",
    ".ts":   "video/mp2t",
    ".mp4":  "video/mp4",
}


def _extract_token(request) -> str | None:
    if "token" in request.query_params:
        return request.query_params["token"]
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth.removeprefix("Bearer ").strip()
    return None


def _resolve_asset(content_type: str, ident: str | int) -> tuple[VideoAsset, int]:
    if content_type == "movie":
        movie = get_object_or_404(Movie, slug=ident, status=PublishStatus.PUBLISHED)
        asset = (
            VideoAsset.objects
            .filter(movie=movie, status=VideoAsset.Status.READY)
            .order_by("-created_at")
            .first()
        )
        if not asset:
            raise Http404("No streamable asset.")
        return asset, movie.id
    else:
        episode = get_object_or_404(
            Episode, pk=ident,
            status=PublishStatus.PUBLISHED,
            season__series__status=PublishStatus.PUBLISHED,
        )
        asset = (
            VideoAsset.objects
            .filter(episode=episode, status=VideoAsset.Status.READY)
            .order_by("-created_at")
            .first()
        )
        if not asset:
            raise Http404("No streamable asset.")
        return asset, episode.id


def _validate_and_check_token(request, *, content_type: str, content_id: int) -> Response | None:
    token = _extract_token(request)
    if not token:
        return Response(
            {"detail": "Playback token required."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    try:
        verify_playback_token(
            token,
            expected_content_type=content_type,
            expected_content_id=content_id,
        )
    except jwt.ExpiredSignatureError:
        return Response(
            {"detail": "Playback token expired."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    except jwt.InvalidTokenError:
        return Response(
            {"detail": "Invalid playback token."},
            status=status.HTTP_403_FORBIDDEN,
        )
    return None


def _resolve_path(asset: VideoAsset, rel_parts: list[str]) -> Path:
    """Validate the path is inside the asset's HLS dir and exists."""
    hls_root = asset.hls_dir_abs()
    target = hls_root.joinpath(*rel_parts).resolve()

    try:
        target.relative_to(hls_root.resolve())
    except ValueError:
        raise Http404("Invalid path.")

    if not target.is_file():
        raise Http404("Not found.")

    return target


def _rewrite_playlist(original: str, token: str) -> str:
    """
    Rewrite a manifest so that every URL a player will fetch from it carries
    the token. Comments (#...) pass through. Non-empty non-comment lines get
    `?token=...` appended (or `&token=...` if the URL already has a query).
    """
    out_lines = []
    for line in original.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            out_lines.append(line)
            continue
        # Append token, preserving any existing query string
        sep = "&" if "?" in stripped else "?"
        out_lines.append(f"{stripped}{sep}{urlencode({'token': token})}")
    return "\n".join(out_lines) + "\n"


def _serve_playlist(asset: VideoAsset, rel_parts: list[str], token: str) -> HttpResponse:
    target = _resolve_path(asset, rel_parts)
    content = target.read_text(encoding="utf-8")
    rewritten = _rewrite_playlist(content, token)
    return HttpResponse(
        rewritten,
        content_type=MIME_BY_EXT[".m3u8"],
    )


def _serve_binary(asset: VideoAsset, rel_parts: list[str]) -> FileResponse:
    target = _resolve_path(asset, rel_parts)
    ext = target.suffix.lower()
    if ext not in MIME_BY_EXT:
        raise Http404("Unsupported file type.")
    return FileResponse(open(target, "rb"), content_type=MIME_BY_EXT[ext])


class _BaseStreamView(APIView):
    permission_classes = [permissions.AllowAny]
    content_type: str = ""

    def get(self, request, ident, rendition: str | None = None, file: str | None = None):
        asset, content_id = _resolve_asset(self.content_type, ident)

        err = _validate_and_check_token(
            request, content_type=self.content_type, content_id=content_id,
        )
        if err is not None:
            return err

        token = _extract_token(request)  # known non-None at this point

        if rendition is None:
            # master manifest — rewrite variant URLs with token
            return _serve_playlist(asset, ["master.m3u8"], token)

        if not RENDITION_RE.match(rendition):
            return Response(
                {"detail": "Invalid rendition name."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not FILE_RE.match(file or ""):
            return Response(
                {"detail": "Invalid file name."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (file or "").endswith(".m3u8"):
            # variant manifest — rewrite segment URLs with token
            return _serve_playlist(asset, [rendition, file], token)
        else:
            # segment / binary — serve as-is
            return _serve_binary(asset, [rendition, file])


class MovieStreamView(_BaseStreamView):
    content_type = "movie"


class EpisodeStreamView(_BaseStreamView):
    content_type = "episode"
