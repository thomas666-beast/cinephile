from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views
from . import auth_views
from subscriptions import views as subscription_views
from . import playback_views
from . import admin_views

app_name = "api-v1"

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

    # Playback
    path("playback/movies/<slug:slug>/", playback_views.MoviePlaybackAPIView.as_view(), name="playback-movie"),
    path("playback/episodes/<int:pk>/", playback_views.EpisodePlaybackAPIView.as_view(), name="playback-episode"),

    # Video
    path("admin/videos/", admin_views.VideoUploadAPIView.as_view(), name="admin-video-upload"),
    path("admin/videos/<int:pk>/complete/", admin_views.CompleteVideoUploadAPIView.as_view(), name="admin-video-complete"),
]
