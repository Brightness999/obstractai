import os
from django.contrib import admin

# Register your models here.
from .models import *
import djstripe, stripe

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
	list_display = ('id', 'attribute', 'value', 'api_attribute', 'api_value', 'words_matched')

	def save_model(self, request, obj, form, change):
		# GlobalAttributes.save()
		# if not change:
		# 	print(GlobalAttributes.id)
		# if not 'id' in form.cleaned_data:
		# 	new = super().save_model(request, obj, form, change)
		# 	print(new)
		super().save_model(request, obj, form, change)
		if not change:
			for group in IntelGroups.objects.all():
				GroupGlobalAttributes.objects.create(intelgroup_id=group.id, globalattribute_id=GlobalAttributes.objects.last().id, isenable=True)
		return True


@admin.register(GroupPlan)
class GroupPlanAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'annual_amount', 'monthly_amount', 'active', 'max_users', 'max_feeds', 'custom_feeds', 'custom_observables', 'api_access' )

	def save_model(self, request, obj, form, change):
		stripe.api_key = os.environ.get("STRIPE_TEST_SECRET_KEY")
		new_product=stripe.Product.create(
			name=form.cleaned_data['name'],
			description=form.cleaned_data['description'],
			active= form.cleaned_data['active'],
			metadata={
				'max_users':form.cleaned_data['max_users'],
				'max_feeds':form.cleaned_data['max_feeds'],
				'custom_feeds':form.cleaned_data['custom_feeds'],
				'custom_observables':form.cleaned_data['custom_observables'],
				'api_access':form.cleaned_data['api_access']
			}
		)
		stripe.Plan.create(
			amount=form.cleaned_data['annual_amount'],
			currency="usd",
			interval="year",
			product=new_product.id,
			billing_scheme="per_unit",
			interval_count=1
		)
		stripe.Plan.create(
			amount=form.cleaned_data['monthly_amount'],
			currency="usd",
			interval="month",
			product=new_product.id,
			billing_scheme="per_unit",
			interval_count=1
		)
		super().save_model(request, obj, form, change)

		return True
