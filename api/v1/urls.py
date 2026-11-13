from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views
from . import auth_views
from subscriptions import views as subscription_views
from . import admin_views
from . import playback_views, stream_views

from . import search_views

from rest_framework.routers import DefaultRouter
from .admin_content_views import (
    AdminGenreViewSet, AdminMovieViewSet, AdminSeriesViewSet,
    AdminSeasonViewSet, AdminEpisodeViewSet, AdminStatsAPIView,
)

app_name = "api-v1"


router = DefaultRouter()
router.register("admin/movies", AdminMovieViewSet, basename="admin-movie")
router.register("admin/series", AdminSeriesViewSet, basename="admin-series")
router.register("admin/seasons", AdminSeasonViewSet, basename="admin-season")
router.register("admin/episodes", AdminEpisodeViewSet, basename="admin-episode")
router.register("admin/genres", AdminGenreViewSet, basename="admin-genre")

urlpatterns = [
    # Catalog
    path("movies/", views.MovieListAPIView.as_view(), name="movie-list"),
    path("movies/<slug:slug>/", views.MovieDetailAPIView.as_view(), name="movie-detail"),
    path("series/", views.SeriesListAPIView.as_view(), name="series-list"),
    path("series/<slug:slug>/", views.SeriesDetailAPIView.as_view(), name="series-detail"),
    path("genres/", views.GenreListAPIView.as_view(), name="genre-list"),
    path("home/", views.HomeAPIView.as_view(), name="home"),

    # Auth
    path("auth/register/", auth_views.RegisterAPIView.as_view(), name="auth-register"),
    path("auth/token/", TokenObtainPairView.as_view(), name="auth-token"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="auth-token-refresh"),
    path("auth/logout/", auth_views.LogoutAPIView.as_view(), name="auth-logout"),
    path("auth/me/", auth_views.MeAPIView.as_view(), name="auth-me"),

    # Subscriptions
    path("plans/", subscription_views.PlanListAPIView.as_view(), name="plan-list"),
    path("subscriptions/", subscription_views.CreateSubscriptionAPIView.as_view(), name="subscription-create"),
    path("subscriptions/me/", subscription_views.MySubscriptionAPIView.as_view(), name="subscription-me"),
    path(
     "subscriptions/<int:pk>/cancel/",
     subscription_views.CancelSubscriptionAPIView.as_view(),
     name="subscription-cancel",
    ),

    # Playback
    path("playback/movies/<slug:slug>/", playback_views.MoviePlaybackAPIView.as_view(), name="playback-movie"),
    path("playback/episodes/<int:pk>/", playback_views.EpisodePlaybackAPIView.as_view(), name="playback-episode"),

    # Video
    path("admin/videos/", admin_views.VideoUploadAPIView.as_view(), name="admin-video-upload"),
    path("admin/videos/<int:pk>/complete/", admin_views.CompleteVideoUploadAPIView.as_view(), name="admin-video-complete"),

    # Playback (issue token + manifest URL)
    path("playback/movies/<slug:slug>/", playback_views.MoviePlaybackAPIView.as_view(), name="playback-movie"),
    path("playback/episodes/<int:pk>/", playback_views.EpisodePlaybackAPIView.as_view(), name="playback-episode"),

    # Stream (served to the player, token-gated)
    path("playback/stream/movies/<slug:ident>/master.m3u8",
         stream_views.MovieStreamView.as_view(), name="playback-stream-movie-master"),
    path("playback/stream/movies/<slug:ident>/<str:rendition>/<str:file>",
         stream_views.MovieStreamView.as_view(), name="playback-stream-movie-file"),
    path("playback/stream/episodes/<int:ident>/master.m3u8",
         stream_views.EpisodeStreamView.as_view(), name="playback-stream-episode-master"),
    path("playback/stream/episodes/<int:ident>/<str:rendition>/<str:file>",
         stream_views.EpisodeStreamView.as_view(), name="playback-stream-episode-file"),

    # Admin dashboard
    path("admin/stats/", AdminStatsAPIView.as_view(), name="admin-stats"),
    # Admin videos
    path("admin/videos/", admin_views.VideoUploadAPIView.as_view(), name="admin-video-upload"),
    path("admin/videos/<int:pk>/complete/", admin_views.CompleteVideoUploadAPIView.as_view(), name="admin-video-complete"),

     # Search
     path("search/", search_views.SearchAPIView.as_view(), name="search"),

    path("history/progress/", views.SaveWatchProgressAPIView.as_view(), name="history-save"),
    path("history/", views.WatchHistoryAPIView.as_view(), name="history-list"),
] + router.urls
