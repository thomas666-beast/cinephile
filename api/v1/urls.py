from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views
from . import auth_views

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
]
