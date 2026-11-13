import logging
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import VideoAsset
from .tasks import transcode_video_asset

logger = logging.getLogger(__name__)


@receiver(post_save, sender=VideoAsset)
def enqueue_transcode_on_upload(sender, instance: VideoAsset, created, **kwargs):
    """
    When a VideoAsset lands in status UPLOADED, enqueue transcoding.
    Wrap in transaction.on_commit so the worker never sees a half-written row.
    """
    if instance.status != VideoAsset.Status.UPLOADED:
        return
    # Avoid re-enqueueing on every save of a still-uploaded asset:
    # we only auto-fire on the transition where the file is present.
    if not instance.video_file:
        return

    def _enqueue():
        try:
            transcode_video_asset.delay(instance.pk)
        except Exception:
            # Queue down? Log and let the retry-via-admin action handle it later.
            logger.exception("Failed to enqueue transcode for asset %s", instance.pk)

    transaction.on_commit(_enqueue)
