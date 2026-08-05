from rest_framework import serializers
from .models import Sticker, StickerCategory


class StickerCategorySerializer(serializers.ModelSerializer):
    sticker_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = StickerCategory
        fields = ['id', 'name', 'slug', 'order', 'sticker_count']


class StickerSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    category_slug = serializers.SlugField(source='category.slug', read_only=True)

    class Meta:
        model = Sticker
        fields = ['id', 'name', 'category', 'category_slug', 'image_url', 'tags']

    def get_image_url(self, obj):
        if not obj.image:
            return ''
        request = self.context.get('request')
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url
