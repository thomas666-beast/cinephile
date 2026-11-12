from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


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
