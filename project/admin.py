from django.contrib import admin

# Register your models here.
from .models import *


@admin.register(Feeds)
class FeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'tags', 'url', 'description', 'intelgroup')


@admin.register(IntelGroups)
class IntelGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'plan')


@admin.register(Attributes)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('attribute', 'value', 'api_attribute', 'api_value', 'words_matched', 'user', 'intelgroup', 'enabled')


