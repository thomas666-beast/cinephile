"""
Reusable factories for creating test objects.
Not a third-party `factory_boy` — just plain functions. Clearer, fewer deps.
"""
import uuid
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from catalog.models import Genre, Movie, Series, Season, Episode, PublishStatus, VideoAsset
from subscriptions.models import SubscriptionPlan, Subscription

User = get_user_model()


def make_user(*, email=None, password="TestPass123!", role=None, is_staff=False, is_superuser=False):
    email = email or f"user-{uuid.uuid4().hex[:8]}@example.com"
    return User.objects.create_user(
        email=email,
        password=password,
        role=role or User.Role.VIEWER,
        is_staff=is_staff,
        is_superuser=is_superuser,
    )


def make_admin(**kwargs):
    kwargs.setdefault("role", User.Role.ADMIN)
    kwargs.setdefault("is_staff", True)
    return make_user(**kwargs)


def make_genre(name="Sci-Fi"):
    return Genre.objects.create(name=name)


def make_movie(*, title="Test Movie", status=PublishStatus.PUBLISHED, genres=None):
    movie = Movie.objects.create(title=title, status=status)
    if genres:
        movie.genres.set(genres)
    return movie


def make_series(*, title="Test Series", status=PublishStatus.PUBLISHED, genres=None):
    s = Series.objects.create(title=title, status=status)
    if genres:
        s.genres.set(genres)
    return s


def make_episode(*, series=None, season_number=1, episode_number=1, status=PublishStatus.PUBLISHED):
    series = series or make_series()
    season, _ = Season.objects.get_or_create(series=series, number=season_number)
    return Episode.objects.create(
        season=season, number=episode_number,
        title=f"Episode {episode_number}", status=status,
    )


def make_plan(*, name="Monthly", duration_days=30, price_cents=999, is_active=True):
    return SubscriptionPlan.objects.create(
        name=name, duration_days=duration_days,
        price_cents=price_cents, is_active=is_active,
    )


def make_subscription(*, user, plan=None, expired=False):
    plan = plan or make_plan()
    now = timezone.now()
    delta = -timedelta(days=1) if expired else timedelta(days=plan.duration_days)
    return Subscription.objects.create(
        user=user, plan=plan,
        status=Subscription.Status.ACTIVE,
        expires_at=now + delta,
    )


def make_video_asset(*, movie=None, episode=None, status=VideoAsset.Status.READY):
    """
    Creates a VideoAsset with a dummy file at MEDIA_ROOT.
    Status defaults to READY (test mode) so playback tests don't need FFmpeg.
    """
    if (movie is None) == (episode is None):
        raise ValueError("Provide exactly one of movie or episode.")
    from django.core.files.base import ContentFile
    asset = VideoAsset(movie=movie, episode=episode, status=status)
    asset.video_file.save(f"test-{uuid.uuid4().hex[:6]}.mp4", ContentFile(b"dummy"), save=False)
    asset.save()
    return asset


def make_hls_files(asset):
    """
    Create a fake HLS output tree for `asset` so stream tests can serve files.
    """
    from pathlib import Path
    from django.conf import settings
    root = Path(settings.MEDIA_ROOT) / asset.hls_root()
    (root / "360p").mkdir(parents=True, exist_ok=True)
    (root / "720p").mkdir(parents=True, exist_ok=True)

    (root / "master.m3u8").write_text(
        "#EXTM3U\n#EXT-X-VERSION:3\n"
        "#EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=640x360\n360p/index.m3u8\n"
        "#EXT-X-STREAM-INF:BANDWIDTH=3000000,RESOLUTION=1280x720\n720p/index.m3u8\n"
    )
    for variant in ("360p", "720p"):
        (root / variant / "index.m3u8").write_text(
            "#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:6\n"
            "#EXTINF:6.0,\nseg_000.ts\n#EXT-X-ENDLIST\n"
        )
        (root / variant / "seg_000.ts").write_bytes(b"\x47" * 188)

    asset.hls_manifest_path = str((root / "master.m3u8").relative_to(settings.MEDIA_ROOT))
    asset.save(update_fields=["hls_manifest_path"])
    return root
