from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser
{% set user_subscriptions_enabled = cookiecutter.use_subscriptions == 'y' and cookiecutter.use_teams != 'y' %}

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display{% if user_subscriptions_enabled %} + ('subscription',){% endif %}

    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('avatar',{% if user_subscriptions_enabled %} 'subscription'{% endif %})
        }),
    )
