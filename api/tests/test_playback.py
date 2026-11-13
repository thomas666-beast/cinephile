from unittest.mock import patch

from django.urls import reverse
from rest_framework.test import APITestCase

from api.tests.base import MediaRootTestCase
from api.tests.factories import (
    make_user, make_plan, make_subscription, make_movie, make_episode,
    make_video_asset, make_hls_files,
)
from catalog.models import VideoAsset


class PlaybackGateTests(APITestCase):
    """IsSubscriber gate: 401 anonymous, 403 authenticated-unsubscribed, 200 subscriber."""

    def setUp(self):
        self.movie = make_movie(title="Gate Test")
        self.asset = make_video_asset(movie=self.movie)
        self.url = reverse("v1:playback-movie", args=[self.movie.slug])

    def test_anonymous_401(self):
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 401)

    def test_unsubscribed_403(self):
        user = make_user()
        self.client.force_authenticate(user)
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 403)

    def test_subscribed_200(self):
        user = make_user()
        plan = make_plan()
        make_subscription(user=user, plan=plan)
        self.client.force_authenticate(user)
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("token", resp.data)


class PlaybackNonReadyTests(APITestCase):
    def test_processing_asset_returns_409(self):
        user = make_user()
        plan = make_plan()
        make_subscription(user=user, plan=plan)
        movie = make_movie(title="Processing")
        make_video_asset(movie=movie, status=VideoAsset.Status.PROCESSING)
        self.client.force_authenticate(user)
        resp = self.client.post(reverse("v1:playback-movie", args=[movie.slug]))
        self.assertEqual(resp.status_code, 409)


class PlaybackTokenBindingTests(MediaRootTestCase):
    def test_token_rejects_other_content(self):
        # Setup: subscriber, two movies, both ready
        user = make_user()
        plan = make_plan()
        make_subscription(user=user, plan=plan)
        m1 = make_movie(title="First")
        m2 = make_movie(title="Second")
        a1 = make_video_asset(movie=m1)
        a2 = make_video_asset(movie=m2)
        make_hls_files(a1)
        make_hls_files(a2)

        self.client.force_authenticate(user)
        resp = self.client.post(reverse("v1:playback-movie", args=[m1.slug]))
        token = resp.data["token"]

        # Use m1's token to fetch m2's manifest — must fail
        stream_url = reverse("v1:playback-stream-movie-master", args=[m2.slug])
        resp = self.client.get(stream_url, {"token": token})
        self.assertEqual(resp.status_code, 403)

    def test_token_serves_correct_content(self):
        user = make_user()
        plan = make_plan()
        make_subscription(user=user, plan=plan)
        m = make_movie(title="Served")
        asset = make_video_asset(movie=m)
        make_hls_files(asset)

        self.client.force_authenticate(user)
        resp = self.client.post(reverse("v1:playback-movie", args=[m.slug]))
        token = resp.data["token"]

        stream_url = reverse("v1:playback-stream-movie-master", args=[m.slug])
        resp = self.client.get(stream_url, {"token": token})
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode()
        self.assertIn("#EXTM3U", body)


class StreamSecurityTests(MediaRootTestCase):
    def setUp(self):
        user = make_user()
        plan = make_plan()
        make_subscription(user=user, plan=plan)
        self.movie = make_movie(title="Secure")
        self.asset = make_video_asset(movie=self.movie)
        make_hls_files(self.asset)
        self.client.force_authenticate(user)
        self.token = self.client.post(
            reverse("v1:playback-movie", args=[self.movie.slug])
        ).data["token"]
        self.stream_url = reverse("v1:playback-stream-movie-master", args=[self.movie.slug])

    def test_no_token_401(self):
        resp = self.client.get(self.stream_url)
        self.assertEqual(resp.status_code, 401)

    def test_bad_token_403(self):
        resp = self.client.get(self.stream_url, {"token": "garbage"})
        self.assertEqual(resp.status_code, 403)

    def test_path_traversal_blocked(self):
        bad = reverse(
            "v1:playback-stream-movie-file",
            args=[self.movie.slug, "..%2f", "passwd"],
        )
        resp = self.client.get(bad, {"token": self.token})
        # Django may return 400 (bad request, route didn't match) or 404. Either is fine.
        self.assertIn(resp.status_code, (400, 404))


class PlaylistRewriteTests(MediaRootTestCase):
    def test_master_manifest_embeds_token_in_variant_urls(self):
        user = make_user()
        make_subscription(user=user, plan=make_plan())
        movie = make_movie(title="Rewrite Test")
        asset = make_video_asset(movie=movie)
        make_hls_files(asset)

        self.client.force_authenticate(user)
        resp = self.client.post(reverse("v1:playback-movie", args=[movie.slug]))
        token = resp.data["token"]

        stream_url = reverse("v1:playback-stream-movie-master", args=[movie.slug])
        resp = self.client.get(stream_url, {"token": token})
        body = resp.content.decode()

        for line in body.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                self.assertIn(f"token={token}", line,
                            f"Manifest URL missing token: {line!r}")

    def test_variant_manifest_embeds_token_in_segment_urls(self):
        user = make_user()
        make_subscription(user=user, plan=make_plan())
        movie = make_movie(title="Variant Rewrite")
        asset = make_video_asset(movie=movie)
        make_hls_files(asset)

        self.client.force_authenticate(user)
        resp = self.client.post(reverse("v1:playback-movie", args=[movie.slug]))
        token = resp.data["token"]

        variant_url = reverse(
            "v1:playback-stream-movie-file",
            args=[movie.slug, "360p", "index.m3u8"],
        )
        resp = self.client.get(variant_url, {"token": token})
        body = resp.content.decode()

        for line in body.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                self.assertIn(f"token={token}", line,
                            f"Variant URL missing token: {line!r}")

    def test_segment_serves_binary(self):
        user = make_user()
        make_subscription(user=user, plan=make_plan())
        movie = make_movie(title="Segment Test")
        asset = make_video_asset(movie=movie)
        make_hls_files(asset)

        self.client.force_authenticate(user)
        resp = self.client.post(reverse("v1:playback-movie", args=[movie.slug]))
        token = resp.data["token"]

        seg_url = reverse(
            "v1:playback-stream-movie-file",
            args=[movie.slug, "360p", "seg_000.ts"],
        )
        resp = self.client.get(seg_url, {"token": token})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "video/mp2t")
        # FileResponse is streaming — this attribute exists on it
        data = b"".join(resp.streaming_content)
        self.assertGreater(len(data), 0)
