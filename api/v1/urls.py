from django.urls import path
from . import views

app_name = "api-v1"

urlpatterns = [
    path("movies/", views.MovieListAPIView.as_view(), name="movie-list"),
    path("movies/<slug:slug>/", views.MovieDetailAPIView.as_view(), name="movie-detail"),
    path("series/", views.SeriesListAPIView.as_view(), name="series-list"),
    path("series/<slug:slug>/", views.SeriesDetailAPIView.as_view(), name="series-detail"),
    path("genres/", views.GenreListAPIView.as_view(), name="genre-list"),
    path("home/", views.HomeAPIView.as_view(), name="home"),
]
