from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profiles",
    )
    name = models.CharField(max_length=50)
    is_kids = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_profile_name_per_user",
            ),
        ]

    def __str__(self):
        return f"{self.user.email} — {self.name}"

    @property
    def initial(self) -> str:
        return (self.name[:1] or "?").upper()
