from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from catalog.models import Movie, Series, PublishStatus
from .serializers import MovieListSerializer, SeriesListSerializer


class SearchPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50


class SearchAPIView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    pagination_class = SearchPagination

    def get(self, request):
        query = (request.query_params.get("q") or "").strip()
        search_type = request.query_params.get("type") or "all"

        if not query:
            return Response({
                "query": "",
                "type": search_type,
                "movies": {"count": 0, "results": []},
                "series": {"count": 0, "results": []},
            })

        movies_qs = Movie.objects.filter(
            status=PublishStatus.PUBLISHED,
        ).filter(
            Q(title__icontains=query) | Q(synopsis__icontains=query)
        ).prefetch_related("genres").order_by("-published_at")

        series_qs = Series.objects.filter(
            status=PublishStatus.PUBLISHED,
        ).filter(
            Q(title__icontains=query) | Q(synopsis__icontains=query)
        ).prefetch_related("genres").order_by("-published_at")

        # Don't query the type we're not returning.
        if search_type == "movie":
            series_qs = series_qs.none()
        elif search_type == "series":
            movies_qs = movies_qs.none()

        # Manually paginate — the response is a combined structure, so we
        # return per-type counts + the current page of each type's results.
        paginator = self.pagination_class()
        movie_page = paginator.paginate_queryset(movies_qs, request)
        series_page = paginator.paginate_queryset(series_qs, request)

        ctx = {"request": request}
        return Response({
            "query": query,
            "type": search_type,
            "movies": {
                "count": movies_qs.count(),
                "results": MovieListSerializer(movie_page, many=True, context=ctx).data,
            },
            "series": {
                "count": series_qs.count(),
                "results": SeriesListSerializer(series_page, many=True, context=ctx).data,
            },
        })
