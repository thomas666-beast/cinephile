from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from api.tests.factories import make_genre, make_movie, make_series, make_episode
from catalog.models import Genre, Movie, Series, Episode, PublishStatus


class SlugTests(TestCase):
    def test_movie_slug_auto_generated(self):
        m = Movie.objects.create(title="The Grand Budapest Hotel")
        self.assertEqual(m.slug, "the-grand-budapest-hotel")

    def test_series_slug_auto_generated(self):
        s = Series.objects.create(title="Twin Peaks")
        self.assertEqual(s.slug, "twin-peaks")

    def test_genre_slug_auto_generated(self):
        g = Genre.objects.create(name="Film Noir")
        self.assertEqual(g.slug, "film-noir")

    def test_manual_slug_preserved(self):
        m = Movie.objects.create(title="Inception", slug="custom-inception")
        self.assertEqual(m.slug, "custom-inception")


class PublishedAtTests(TestCase):
    def test_draft_has_no_published_at(self):
        m = Movie.objects.create(title="Draft", status=PublishStatus.DRAFT)
        self.assertIsNone(m.published_at)

    def test_publishing_sets_published_at(self):
        m = Movie.objects.create(title="Release", status=PublishStatus.PUBLISHED)
        self.assertIsNotNone(m.published_at)

    def test_unpublishing_keeps_published_at(self):
        m = Movie.objects.create(title="Release", status=PublishStatus.PUBLISHED)
        first = m.published_at
        m.status = PublishStatus.DRAFT
        m.save()
        self.assertEqual(m.published_at, first)


class SeriesEpisodeHierarchyTests(TestCase):
    def test_season_number_unique_per_series(self):
        s = make_series()
        make_episode(series=s, season_number=1)
        # Duplicate season creation — should fail because of unique_together
        from catalog.models import Season
        with self.assertRaises(IntegrityError):
            Season.objects.create(series=s, number=1)

    def test_episode_number_unique_per_season(self):
        e1 = make_episode(episode_number=1)
        with self.assertRaises(IntegrityError):
            Episode.objects.create(season=e1.season, number=1, title="Dup")
