from django.db import IntegrityError
from django.test import TestCase

from api.tests.base import MediaRootTestCase
from api.tests.factories import make_movie, make_episode, make_video_asset
from catalog.models import VideoAsset


class VideoAssetConstraintTests(TestCase):
    def test_requires_exactly_one_parent(self):
        with self.assertRaises(IntegrityError):
            VideoAsset.objects.create()  # no movie, no episode

    def test_rejects_both_parents(self):
        m = make_movie()
        e = make_episode()
        with self.assertRaises(IntegrityError):
            VideoAsset.objects.create(movie=m, episode=e)


class VideoAssetFileTests(MediaRootTestCase):
    def test_upload_sets_metadata_and_status(self):
        m = make_movie()
        asset = make_video_asset(movie=m)
        self.assertEqual(asset.status, VideoAsset.Status.READY)  # we set it explicitly in factory
        self.assertTrue(asset.file_size_bytes > 0)
        self.assertTrue(asset.original_filename.endswith(".mp4"))

    def test_content_type_property(self):
        m = make_movie()
        asset = make_video_asset(movie=m)
        self.assertEqual(asset.content_type, "movie")
        self.assertEqual(asset.content_id, m.id)
