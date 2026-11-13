from unittest.mock import patch
from pathlib import Path

from api.tests.base import MediaRootTestCase
from api.tests.factories import make_movie, make_video_asset
from catalog.models import VideoAsset
from catalog.tasks import transcode_video_asset


class TranscodeTaskTests(MediaRootTestCase):
    def test_success_transitions_to_ready(self):
        m = make_movie()
        asset = make_video_asset(movie=m, status=VideoAsset.Status.UPLOADED)

        # Patch `transcode` to create a fake master.m3u8 and return its path.
        def fake_transcode(source_path, out_dir):
            out_dir.mkdir(parents=True, exist_ok=True)
            master = out_dir / "master.m3u8"
            master.write_text("#EXTM3U\n")
            return master

        with patch("catalog.tasks.transcode", side_effect=fake_transcode):
            transcode_video_asset(asset.pk)

        asset.refresh_from_db()
        self.assertEqual(asset.status, VideoAsset.Status.READY)
        self.assertTrue(asset.hls_manifest_path.endswith("master.m3u8"))

    def test_failure_transitions_to_failed(self):
        m = make_movie()
        asset = make_video_asset(movie=m, status=VideoAsset.Status.UPLOADED)

        from catalog.transcoding import TranscodeError
        with patch("catalog.tasks.transcode", side_effect=TranscodeError("invalid data")):
            transcode_video_asset(asset.pk)

        asset.refresh_from_db()
        self.assertEqual(asset.status, VideoAsset.Status.FAILED)
        self.assertIn("invalid data", asset.processing_error)
