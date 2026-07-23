from django.db import models

# Create your models here.
class StickerCategory(models.Model):
    """
    Group of stickers shown together in the editor's sticker drawer dropdown
    (e.g. 'Babies', 'Wedding', 'Birthday'). Admin-managed.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sticker_categories'
        ordering = ['order', 'name']
        verbose_name_plural = 'sticker categories'

    def __str__(self):
        return self.name

    @property
    def sticker_count(self):
        return self.stickers.filter(is_active=True).count()


class Sticker(models.Model):
    """
    A single PNG sticker the user can drop onto a canvas. Admins upload these
    one at a time (or in bulk via the changelist). The editor's drawer queries
    these by category + search term.
    """
    category = models.ForeignKey(
        StickerCategory,
        on_delete=models.CASCADE,
        related_name='stickers',
    )
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to='stickers/')
    tags = models.JSONField(default=list, blank=True, help_text='Optional search keywords, e.g. ["bear","teddy","cute"]')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stickers'
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['category', 'is_active']),
        ]

    def __str__(self):
        return f"{self.category.name} · {self.name}"
