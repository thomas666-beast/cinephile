from django.contrib import admin
from .models import Genre, Movie, Series, Season, Episode


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "release_year", "status", "published_at", "duration_minutes")
    list_filter = ("status", "genres", "release_year")
    search_fields = ("title", "synopsis")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("genres",)
    date_hierarchy = "created_at"
    fieldsets = (
        (None, {"fields": ("title", "slug", "synopsis")}),
        ("Details", {"fields": ("release_year", "duration_minutes", "genres")}),
        ("Media", {"fields": ("poster", "backdrop")}),
        ("Publishing", {"fields": ("status", "published_at")}),
    )


class SeasonInline(admin.TabularInline):
    model = Season
    extra = 0
    fields = ("number", "title")


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ("title", "start_year", "end_year", "status", "published_at")
    list_filter = ("status", "genres", "start_year")
    search_fields = ("title", "synopsis")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("genres",)
    inlines = [SeasonInline]
    fieldsets = (
        (None, {"fields": ("title", "slug", "synopsis")}),
        ("Details", {"fields": ("start_year", "end_year", "genres")}),
        ("Media", {"fields": ("poster", "backdrop")}),
        ("Publishing", {"fields": ("status", "published_at")}),
    )


class EpisodeInline(admin.TabularInline):
    model = Episode
    extra = 0
    fields = ("number", "title", "duration_minutes", "status")


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ("__str__", "series", "number", "title")
    list_filter = ("series",)
    search_fields = ("series__title", "title")
    inlines = [EpisodeInline]


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ("__str__", "season", "number", "title", "status", "air_date")
    list_filter = ("status", "season__series")
    search_fields = ("title", "synopsis", "season__series__title")
    date_hierarchy = "created_at"
