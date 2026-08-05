from django.contrib import admin, messages
from django import forms
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from .models import Sticker, StickerCategory

# Register your models here.

class StickerInline(TabularInline):
    model = Sticker
    extra = 0
    fields = ['image', 'name', 'order', 'is_active'] # image → lets the admin upload/change the file
    readonly_fields = ['image_thumb'] # image_thumb → shows a preview, but only as a read-only display

    def image_thumb(self, obj): # A function to show the preview of the sticker in the table
        if not obj.image:
            return '—'
        return format_html(
            '<img src="{}" style="width:48px;height:48px;object-fit:contain;'
            'background:#f8fafc;border:1px solid #e5e7eb;border-radius:6px;" />',
            obj.image.url,
        )
    image_thumb.short_description = 'Preview'

@admin.register(StickerCategory)
class StickerCategoryAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'order', 'sticker_count', 'is_active']
    list_display_links = ['name']
    list_filter = ['is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [StickerInline]

class MultipleFileInput(forms.ClearableFileInput):
    """
    Django 4.2+ refuses to render `ClearableFileInput` with `multiple=True`
    via system checks (W901/E901) — it can't round-trip an initial file when
    multiple selection is involved. The supported pattern is a subclass that
    opts in via `allow_multiple_selected = True` and a matching field that
    returns the list. See https://docs.djangoproject.com/en/5.1/topics/http/file-uploads/#uploading-multiple-files
    """
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput(attrs={'multiple': True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single = super().clean
        if isinstance(data, (list, tuple)):
            return [single(d, initial) for d in data]
        return single(data, initial)


class BulkUploadForm(forms.Form):
    """Lets an admin drop in many PNGs at once and have one Sticker row created
    per file, with the filename (sans extension) used as the sticker name."""
    category = forms.ModelChoiceField(
        queryset=StickerCategory.objects.filter(is_active=True),
        help_text='All uploaded PNGs land in this category.',
    )
    files = MultipleFileField(
        required=True,
        help_text='Select multiple PNGs. Filename becomes the sticker name.',
    )


@admin.register(Sticker)
class StickerAdmin(ModelAdmin):
    list_display = ['image_thumb', 'name', 'category', 'order', 'is_active', 'created_at']
    list_display_links = ['image_thumb', 'name']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'tags']
    autocomplete_fields = ['category']
    list_per_page = 60

    def image_thumb(self, obj):
        if not obj.image:
            return format_html('<div style="width:{}px;height:{}px;background:{};border-radius:6px;"></div>', 48, 48, "#f3f4f6")
        return format_html(
            '<img src="{}" style="width:48px;height:48px;object-fit:contain;'
            'background:#f8fafc;border:1px solid #e5e7eb;border-radius:6px;" />',
            obj.image.url,
        )
    image_thumb.short_description = 'Preview'

    # ── Bulk upload action ──────────────────────────────────────────────────
    # Lives on the changelist; lets admins ingest a whole sticker pack with
    # one form post instead of clicking "Add sticker" 30 times in a row.

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom = [
            path('bulk-upload/', self.admin_site.admin_view(self.bulk_upload_view), name='stickers_sticker_bulk_upload'),
        ]
        return custom + urls

    def bulk_upload_view(self, request):
        from django.shortcuts import redirect, render

        if request.method == 'POST':
            form = BulkUploadForm(request.POST, request.FILES)
            files = request.FILES.getlist('files')
            if form.is_valid() and files:
                category = form.cleaned_data['category']
                created = 0
                for f in files:
                    name = f.name.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ').strip().title() or 'Sticker'
                    Sticker.objects.create(category=category, name=name, image=f)
                    created += 1
                self.message_user(
                    request,
                    f'Uploaded {created} sticker{"s" if created != 1 else ""} to "{category.name}".',
                    messages.SUCCESS,
                )
                return redirect('admin:stickers_sticker_changelist') 
        else:
            form = BulkUploadForm()

        return render(request, 'admin/stickers/bulk_upload.html', {
            'form': form,
            'opts': self.model._meta,
            'title': 'Bulk upload stickers',
        })