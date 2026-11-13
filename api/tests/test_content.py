from django.urls import reverse
from rest_framework.test import APITestCase

from api.tests.factories import make_movie, make_series, make_episode, make_genre
from catalog.models import PublishStatus


class MovieListTests(APITestCase):
    def test_only_published_visible(self):
        make_movie(title="Public", status=PublishStatus.PUBLISHED)
        make_movie(title="Hidden", status=PublishStatus.DRAFT)
        resp = self.client.get(reverse("v1:movie-list"))
        self.assertEqual(resp.status_code, 200)
        titles = [m["title"] for m in resp.data["results"]]
        self.assertIn("Public", titles)
        self.assertNotIn("Hidden", titles)

    def test_draft_detail_404(self):
        m = make_movie(title="Hidden", status=PublishStatus.DRAFT)
        resp = self.client.get(reverse("v1:movie-detail", args=[m.slug]))
        self.assertEqual(resp.status_code, 404)


class SeriesDetailTests(APITestCase):
    def test_nests_seasons_and_episodes(self):
        s = make_series(title="Nested")
        make_episode(series=s, season_number=1, episode_number=1)
        make_episode(series=s, season_number=1, episode_number=2)
        resp = self.client.get(reverse("v1:series-detail", args=[s.slug]))
        self.assertEqual(resp.status_code, 200)
        seasons = resp.data["seasons"]
        self.assertEqual(len(seasons), 1)
        self.assertEqual(len(seasons[0]["episodes"]), 2)


class GenreListTests(APITestCase):
    def test_lists_genres(self):
        make_genre("Sci-Fi")
        make_genre("Drama")
        resp = self.client.get(reverse("v1:genre-list"))
        self.assertEqual(resp.status_code, 200)
        names = [g["name"] for g in resp.data]
        self.assertIn("Sci-Fi", names)
        self.assertIn("Drama", names)
