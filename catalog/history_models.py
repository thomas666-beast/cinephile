from django.db import models
from django.conf import settings
from django.utils import timezone
from .models import Movie, Episode

class WatchProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="watch_history"
    )
    profile = models.ForeignKey(
        "accounts.Profile",
        on_delete=models.CASCADE,
        related_name="watch_history",
    )
    movie = models.ForeignKey(Movie, null=True, blank=True, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, null=True, blank=True, on_delete=models.CASCADE)
    progress_seconds = models.FloatField(default=0)
    duration_seconds = models.FloatField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(movie__isnull=False, episode__isnull=True)
                    | models.Q(movie__isnull=True, episode__isnull=False)
                ),
                name="watch_progress_exactly_one_content",
            ),
            models.UniqueConstraint(
                fields=["profile", "movie"],
                name="unique_profile_movie_progress",
            ),
            models.UniqueConstraint(
                fields=["profile", "episode"],
                name="unique_profile_episode_progress",
            ),
        ]

    def __str__(self):
        content = self.movie.title if self.movie else f"S{self.episode.season.number}E{self.episode.number}"
        return f"{self.user.email} - {content} ({int(self.progress_seconds)}s)"

    @property
    def percent_complete(self):
        if self.duration_seconds <= 0:
            return 0
        return min(100, (self.progress_seconds / self.duration_seconds) * 100)