from django.contrib import admin
from django.utils.html import format_html

from .admin_mixins import PublishActionsMixin, ThumbnailMixin
from .models import Genre, Movie, Series, Season, Episode


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "movie_count", "series_count")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Movies")
    def movie_count(self, obj):
        return obj.movies.count()

    @admin.display(description="Series")
    def series_count(self, obj):
        return obj.series.count()


@admin.register(Movie)
class MovieAdmin(PublishActionsMixin, ThumbnailMixin, admin.ModelAdmin):
    list_display = (
        "thumbnail", "title", "release_year", "duration_minutes",
        "status", "published_at",
    )
    list_display_links = ("title",)
    list_filter = ("status", "genres", "release_year")
    search_fields = ("title", "synopsis")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("genres",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at", "published_at")
    fieldsets = (
        (None, {"fields": ("title", "slug", "synopsis")}),
        ("Details", {"fields": ("release_year", "duration_minutes", "genres")}),
        ("Media", {"fields": ("poster", "backdrop")}),
        ("Publishing", {"fields": ("status", "published_at")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


class SeasonInline(admin.TabularInline):
    model = Season
    extra = 0
    fields = ("number", "title", "poster")


@admin.register(Series)
class SeriesAdmin(PublishActionsMixin, ThumbnailMixin, admin.ModelAdmin):
    list_display = (
        "thumbnail", "title", "start_year", "end_year",
        "status", "published_at",
    )
    list_display_links = ("title",)
    list_filter = ("status", "genres", "start_year")
    search_fields = ("title", "synopsis")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("genres",)
    readonly_fields = ("created_at", "updated_at", "published_at")
    inlines = [SeasonInline]
    fieldsets = (
        (None, {"fields": ("title", "slug", "synopsis")}),
        ("Details", {"fields": ("start_year", "end_year", "genres")}),
        ("Media", {"fields": ("poster", "backdrop")}),
        ("Publishing", {"fields": ("status", "published_at")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


class EpisodeInline(admin.TabularInline):
    model = Episode
    extra = 0
    fields = ("number", "title", "duration_minutes", "status", "still")


@admin.register(Season)
class SeasonAdmin(ThumbnailMixin, admin.ModelAdmin):
    thumbnail_field = "poster"
    list_display = ("thumbnail", "__str__", "series", "number", "title")
    list_display_links = ("__str__",)
    list_filter = ("series",)
    search_fields = ("series__title", "title")
    readonly_fields = ("created_at", "updated_at")
    inlines = [EpisodeInline]


@admin.register(Episode)
class EpisodeAdmin(PublishActionsMixin, ThumbnailMixin, admin.ModelAdmin):
    thumbnail_field = "still"
    list_display = (
        "thumbnail", "__str__", "season", "number", "title",
        "status", "air_date",
    )
    list_display_links = ("__str__",)
    list_filter = ("status", "season__series")
    search_fields = ("title", "synopsis", "season__series__title", "season__title")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
