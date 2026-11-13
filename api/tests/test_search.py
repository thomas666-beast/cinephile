from django.urls import reverse
from rest_framework.test import APITestCase

from api.tests.factories import make_movie, make_series
from catalog.models import PublishStatus


class SearchAPITests(APITestCase):
    def test_empty_query_returns_empty(self):
        resp = self.client.get(reverse("v1:search"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["movies"]["count"], 0)
        self.assertEqual(resp.data["series"]["count"], 0)

    def test_matches_movie_title(self):
        make_movie(title="Inception", status=PublishStatus.PUBLISHED)
        resp = self.client.get(reverse("v1:search"), {"q": "inception"})
        self.assertEqual(resp.data["movies"]["count"], 1)
        self.assertEqual(resp.data["movies"]["results"][0]["title"], "Inception")

    def test_case_insensitive(self):
        make_movie(title="The Godfather", status=PublishStatus.PUBLISHED)
        resp = self.client.get(reverse("v1:search"), {"q": "GODFATHER"})
        self.assertEqual(resp.data["movies"]["count"], 1)

    def test_matches_synopsis(self):
        m = make_movie(title="Untitled", status=PublishStatus.PUBLISHED)
        m.synopsis = "A quiet story about a lonely lighthouse keeper."
        m.save()
        resp = self.client.get(reverse("v1:search"), {"q": "lighthouse"})
        self.assertEqual(resp.data["movies"]["count"], 1)

    def test_draft_content_hidden(self):
        make_movie(title="Hidden Film", status=PublishStatus.DRAFT)
        resp = self.client.get(reverse("v1:search"), {"q": "hidden"})
        self.assertEqual(resp.data["movies"]["count"], 0)

    def test_filter_by_type_movie(self):
        make_movie(title="Overlap", status=PublishStatus.PUBLISHED)
        make_series(title="Overlap Series", status=PublishStatus.PUBLISHED)
        resp = self.client.get(reverse("v1:search"), {"q": "overlap", "type": "movie"})
        self.assertEqual(resp.data["movies"]["count"], 1)
        self.assertEqual(resp.data["series"]["count"], 0)

    def test_filter_by_type_series(self):
        make_movie(title="Overlap", status=PublishStatus.PUBLISHED)
        make_series(title="Overlap Series", status=PublishStatus.PUBLISHED)
        resp = self.client.get(reverse("v1:search"), {"q": "overlap", "type": "series"})
        self.assertEqual(resp.data["movies"]["count"], 0)
        self.assertEqual(resp.data["series"]["count"], 1)
