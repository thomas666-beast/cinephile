import logging
from pathlib import Path

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from .models import VideoAsset, hls_output_dir
from .transcoding import transcode, TranscodeError

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def transcode_video_asset(self, asset_id: int) -> dict:
    """
    Transcode a VideoAsset's raw file into HLS. Idempotent.
    Returns a dict summary for the result backend (handy for debugging).
    """
    try:
        asset = VideoAsset.objects.get(pk=asset_id)
    except VideoAsset.DoesNotExist:
        logger.warning("transcode_video_asset: asset %s not found", asset_id)
        return {"asset_id": asset_id, "status": "missing"}

    if not asset.video_file:
        _mark_failed(asset, "No video_file on asset.")
        return {"asset_id": asset_id, "status": "failed", "reason": "no_file"}

    if asset.status == VideoAsset.Status.READY:
        return {"asset_id": asset_id, "status": "already_ready"}

    # Move to processing immediately so admin sees the transition.
    asset.status = VideoAsset.Status.PROCESSING
    asset.processing_error = ""
    asset.save(update_fields=["status", "processing_error", "updated_at"])

    source_path = Path(asset.video_file.path)
    out_dir = Path(settings.MEDIA_ROOT) / hls_output_dir(asset)

    try:
        master_path = transcode(source_path, out_dir)
    except TranscodeError as e:
        logger.exception("Transcode failed for asset %s", asset_id)
        _mark_failed(asset, str(e))
        # Retry transient failures, but not permanent ones.
        if self.request.retries < self.max_retries and _is_retryable(str(e)):
            raise self.retry(exc=e)
        return {"asset_id": asset_id, "status": "failed", "reason": str(e)[:200]}
    except Exception as e:
        logger.exception("Unexpected transcode failure for asset %s", asset_id)
        _mark_failed(asset, f"Unexpected: {e}")
        raise

    # Persist the manifest path relative to MEDIA_ROOT so the URL builder can
    # turn it into a MEDIA_URL-based link (and later, a CDN link).
    asset.hls_manifest_path = str(master_path.relative_to(settings.MEDIA_ROOT))
    asset.status = VideoAsset.Status.READY
    asset.processing_error = ""
    asset.save(update_fields=[
        "hls_manifest_path", "status", "processing_error", "updated_at",
    ])
    logger.info("Asset %s ready: %s", asset_id, asset.hls_manifest_path)
    return {"asset_id": asset_id, "status": "ready", "manifest": asset.hls_manifest_path}


def _mark_failed(asset: VideoAsset, message: str) -> None:
    asset.status = VideoAsset.Status.FAILED
    # Cap error length so a runaway FFmpeg stderr doesn't blow the DB row
    asset.processing_error = (message or "")[:4000]
    asset.save(update_fields=["status", "processing_error", "updated_at"])


def _is_retryable(error_message: str) -> bool:
    """Heuristic: retry transient I/O errors, don't retry 'invalid data' errors."""
    lowered = error_message.lower()
    transient = ("timed out", "connection", "temporarily", "disk", "no space")
    permanent = ("invalid data", "could not find codec", "moov atom not found",
                 "no video stream", "corrupt")
    if any(p in lowered for p in permanent):
        return False
    return any(t in lowered for t in transient)
