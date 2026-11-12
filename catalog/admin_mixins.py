from django.contrib import admin
from django.utils.html import format_html


class PublishActionsMixin:
    """Adds bulk publish/unpublish actions. Requires a `status` field."""

    actions = ["make_published", "make_draft"]

    @admin.action(description="Publish selected items")
    def make_published(self, request, queryset):
        from django.utils import timezone
        from .models import PublishStatus

        updated = queryset.update(
            status=PublishStatus.PUBLISHED,
        )
        # Set published_at only for those without it
        queryset.filter(published_at__isnull=True).update(published_at=timezone.now())
        self.message_user(request, f"{updated} item(s) published.")

    @admin.action(description="Move selected items to draft")
    def make_draft(self, request, queryset):
        from .models import PublishStatus

        updated = queryset.update(status=PublishStatus.DRAFT)
        self.message_user(request, f"{updated} item(s) moved to draft.")


class ThumbnailMixin:
    """Adds a small thumbnail column. Expects the model to have `poster` or `still`."""

    thumbnail_field = "poster"  # override in subclasses if needed
    thumbnail_size = 60

    @admin.display(description="")
    def thumbnail(self, obj):
        image = getattr(obj, self.thumbnail_field, None)
        if not image:
            return "—"
        return format_html(
            '<img src="{}" style="height:{}px; border-radius:4px;" />',
            image.url,
            self.thumbnail_size,
        )
