from django.shortcuts import render
from django.db.models import Q
from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination

from .models import Sticker, StickerCategory
from .serializers import StickerSerializer, StickerCategorySerializer


class StickerCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Public read-only list of active sticker categories (admin populates)."""
    queryset = StickerCategory.objects.filter(is_active=True)
    serializer_class = StickerCategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class StickerPagination(PageNumberPagination):
    page_size = 60
    page_size_query_param = 'page_size'
    max_page_size = 200


class StickerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public read-only sticker listing. Filters:
      - ?category=<slug> filters by category slug
      - ?search=<term>   matches name (icontains) or any element of tags

    Pagination is page-based so the drawer can lazily fetch more on scroll.
    """
    serializer_class = StickerSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StickerPagination

    def get_queryset(self):
        qs = Sticker.objects.filter(is_active=True).select_related('category')
        params = self.request.query_params
        category = params.get('category')
        if category:
            qs = qs.filter(category__slug=category)
        search = (params.get('search') or '').strip()
        if search:
            # Match name OR any tag containing the search term. JSONField
            # icontains works for substring matching against the serialized
            # representation, which is good enough for short keyword tags.
            qs = qs.filter(Q(name__icontains=search) | Q(tags__icontains=search))
        return qs
