from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from .models import User


@admin.register(User)
class UserAdmin(ModelAdmin, BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'subscription_plan', 'is_verified', 'created_at']
    list_display_links = ['email', 'first_name', 'last_name', 'role', 'subscription_plan', 'is_verified', 'created_at']
    list_filter = ['role', 'subscription_plan', 'is_verified', 'subscription_end']
    search_fields = ['email', 'first_name', 'last_name']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Pixora', {
            'fields': ('role', 'phone', 'avatar', 'subscription_plan',
                       'subscription_period', 'subscription_start', 'subscription_end', 'is_verified'),
        }),
    )
