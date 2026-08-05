from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('sticker-categories', views.StickerCategoryViewSet, basename='sticker-category')
router.register('stickers', views.StickerViewSet, basename='sticker')

urlpatterns = [
    path('', include(router.urls)),
]
