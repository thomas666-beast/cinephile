from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

import uuid


def video_upload_path(instance, filename):
    """
    Build a deterministic, collision-free path:
      videos/movies/<movie_id>/<uuid>.mp4
      videos/episodes/<episode_id>/<uuid>.mp4
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "mp4"
    parent_type = "movies" if instance.movie_id else "episodes"
    parent_id = instance.movie_id or instance.episode_id
    return f"videos/{parent_type}/{parent_id}/{uuid.uuid4().hex}.{ext}"

def hls_output_dir(instance) -> str:
    """
    Root directory for this asset's HLS output, relative to MEDIA_ROOT.
    Keyed by asset id so re-uploads get distinct output; the previous
    rendition set is cleaned up separately if needed.
    """
    parent_type = "movies" if instance.movie_id else "episodes"
    parent_id = instance.movie_id or instance.episode_id
    return f"hls/{parent_type}/{parent_id}/{instance.pk}"

class PublishStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"


class TimeStampedModel(models.Model):
    """Abstract base: created/updated timestamps for every content model."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Genre(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Movie(TimeStampedModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    synopsis = models.TextField(blank=True)
    release_year = models.PositiveIntegerField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(
        null=True, blank=True, help_text="Runtime in minutes"
    )
    genres = models.ManyToManyField(Genre, related_name="movies", blank=True)
    poster = models.ImageField(upload_to="posters/movies/", null=True, blank=True)
    backdrop = models.ImageField(upload_to="backdrops/movies/", null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=PublishStatus.choices, default=PublishStatus.DRAFT
    )
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-published_at"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == PublishStatus.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("movie-detail", kwargs={"slug": self.slug})


class Series(TimeStampedModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    synopsis = models.TextField(blank=True)
    start_year = models.PositiveIntegerField(null=True, blank=True)
    end_year = models.PositiveIntegerField(null=True, blank=True)
    genres = models.ManyToManyField(Genre, related_name="series", blank=True)
    poster = models.ImageField(upload_to="posters/series/", null=True, blank=True)
    backdrop = models.ImageField(upload_to="backdrops/series/", null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=PublishStatus.choices, default=PublishStatus.DRAFT
    )
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "series"
        indexes = [
            models.Index(fields=["status", "-published_at"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == PublishStatus.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("series-detail", kwargs={"slug": self.slug})


class Season(TimeStampedModel):
    series = models.ForeignKey(Series, related_name="seasons", on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    title = models.CharField(max_length=255, blank=True)
    synopsis = models.TextField(blank=True)
    poster = models.ImageField(upload_to="posters/seasons/", null=True, blank=True)

    class Meta:
        ordering = ["series", "number"]
        unique_together = [("series", "number")]

    def __str__(self):
        return f"{self.series.title} — Season {self.number}"


class Episode(TimeStampedModel):
    season = models.ForeignKey(Season, related_name="episodes", on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    synopsis = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    air_date = models.DateField(null=True, blank=True)
    still = models.ImageField(upload_to="stills/episodes/", null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=PublishStatus.choices, default=PublishStatus.DRAFT
    )

    class Meta:
        ordering = ["season", "number"]
        unique_together = [("season", "number")]

    def __str__(self):
        return f"S{self.season.number:02d}E{self.number:02d} — {self.title}"

class VideoAsset(TimeStampedModel):
    """
    A raw video file attached to a Movie or Episode.
    Stored on local disk for now; swap to S3 by changing `video_file.storage` later.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending upload"
        UPLOADED = "uploaded", "Uploaded"
        PROCESSING = "processing", "Processing"
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"

    movie = models.ForeignKey(
        Movie, null=True, blank=True, on_delete=models.CASCADE, related_name="videos"
    )
    episode = models.ForeignKey(
        Episode, null=True, blank=True, on_delete=models.CASCADE, related_name="videos"
    )

    video_file = models.FileField(upload_to=video_upload_path, max_length=500)
    original_filename = models.CharField(max_length=255, blank=True)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    mime_type = models.CharField(max_length=100, blank=True)

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )

    # Filled in by Task 11 (transcoding)
    hls_manifest_path = models.CharField(max_length=500, blank=True)
    processing_error = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(movie__isnull=False, episode__isnull=True)
                    | models.Q(movie__isnull=True, episode__isnull=False)
                ),
                name="video_asset_exactly_one_parent",
            ),
        ]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["movie", "status"]),
            models.Index(fields=["episode", "status"]),
        ]

    def __str__(self):
        parent = self.movie or self.episode
        return f"Video for {parent} ({self.status})"

    @property
    def content_type(self):
        return "movie" if self.movie_id else "episode"

    @property
    def content_id(self):
        return self.movie_id or self.episode_id

    def save(self, *args, **kwargs):
        # After the file is saved, record its real metadata and mark uploaded.
        if self.video_file and self.video_file.name:
            if not self.original_filename:
                import os
                self.original_filename = os.path.basename(self.video_file.name)
            try:
                self.file_size_bytes = self.video_file.size
            except (OSError, ValueError):
                pass
            if self.status == self.Status.PENDING:
                self.status = self.Status.UPLOADED
        super().save(*args, **kwargs)

        def hls_root(self):
        """Directory (relative to MEDIA_ROOT) where this asset's HLS output lives."""
        return hls_output_dir(self)

    def hls_dir_abs(self):
        """Absolute filesystem path to the asset's HLS output directory."""
        from pathlib import Path
        from django.conf import settings
        return Path(settings.MEDIA_ROOT) / self.hls_root()

    def available_renditions(self) -> list[str]:
        """Subdirectory names containing a valid index.m3u8, ordered smallest→largest."""
        root = self.hls_dir_abs()
        if not root.exists():
            return []
        renditions = []
        for child in root.iterdir():
            if child.is_dir() and (child / "index.m3u8").exists():
                renditions.append(child.name)
        # Sort by numeric prefix if present (360p < 720p < 1080p)
        def _num(name: str) -> int:
            digits = "".join(c for c in name if c.isdigit())
            return int(digits) if digits else 0
        return sorted(renditions, key=_num)
