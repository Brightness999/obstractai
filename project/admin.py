from django.contrib import admin

# Register your models here.
from .models import *
from djstripe.models import Product, Plan, Subscription

@admin.register(Feeds)
class FeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'tags', 'url', 'description', 'intelgroup')


@admin.register(IntelGroups)
class IntelGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'plan')

    readonly_fields = ('name', 'description', 'plan')

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(GlobalAttributes)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('attribute', 'value', 'api_attribute', 'api_value', 'words_matched', 'user', 'intelgroup', 'enabled')

# @admin.register(Plan)
# class PlanAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description', 'active', )

# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ('')