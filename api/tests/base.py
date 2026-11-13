import shutil
import tempfile

from django.test import override_settings
from rest_framework.test import APITestCase


class MediaRootTestCase(APITestCase):
    """
    Base for API tests that touch the filesystem. Each test gets a fresh
    MEDIA_ROOT that's cleaned up afterwards. Uses DRF's APIClient so
    force_authenticate() is available.
    """

    @classmethod
    def setUpClass(cls):
        cls._temp_media = tempfile.mkdtemp(prefix="cinephile-test-media-")
        cls._override = override_settings(MEDIA_ROOT=cls._temp_media)
        cls._override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._override.disable()
        shutil.rmtree(cls._temp_media, ignore_errors=True)
