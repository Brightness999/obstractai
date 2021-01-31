import secrets
import urllib
import xmltodict
import json
import os
import stripe
import string, random

from urllib.parse import urlencode
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from cyobstract import extract
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from itertools import chain
from datetime import datetime, timedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
load_dotenv()
from rest_framework import generics
from apps.users.models import CustomUser
from djstripe.models import Product, Plan, Subscription
from dateutil import parser as dateutil_parser
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from pegasus.apps.examples.tasks import progress_bar_task

from ..models import IntelGroups, APIKeys, WebHooks, UserIntelGroupRoles, FeedChannels, FeedItems, Feeds, GroupGlobalAttributes, \
	Categories, UserIntelGroupRoles, Indicators, Tags, GlobalIndicators, Whitelists, APIKeys, GlobalAttributes, Attributes, PlanHistory, IntelReports
from ..serializers import RoleGroupSerializer, UserSerializer, GroupAPIkeySerializer, GroupWebHookSerializer, FeedCategorySerializer, \
	CategorySerializer, FeedItemSerializer, ItemIndicatorSerializer, FeedChannelSerializer, \
		TagSerializer, GlobalIndicatorSerializer, UserGroupRoleSerializer, IndicatorGlobalSerializer, UserIndicatorWhitelistSerializer, \
			GlobalItemIndicatorSerializer, UserIntelGroupRolesSerializer, GroupCategoryFeedSerializer, GroupRoleSerializer, \
				UserGroupAttributeSerializer, CustomUserSerializer, IntelGroupSerializer, \
					UserGlobalIndicatorSerializer, CommentSerializer, ChangeEmailSerializer, IDSerializer, AccepInviteSerializer, AttributeCreateSerializer, AttributeUpdateSerializer, \
						CategoryUpdateSerializer, ManageEnabledSerializer,FeedCreateSerializer,FeedUpdateSerializer,GlobalAttributeCreateSerializer,GlobalAttributeUpdateSerializer, \
							GlobalIndicatorCreateSerializer,EnabledSerializer,IntelgroupCreateSerializer,InviteSerializer,RoleUpdateSerializer,SearchFeedSerializer,SearchReportSerializer, \
								WebhookCreateSerializer,WebhookUpdateSerializer,WhitelistCreateSerializer, APIKeyCreateSerializer, CategoryCreateSerializer, IntelgroupUpdateSerializer, \
									ItemFeedGroupReportSerializer, GroupGlobalAttributeSerializer, GlobalAttributeSerializer

@csrf_exempt
def apifeeds(request):
	body_unicode = request.body.decode('utf-8')
	body = json.loads(body_unicode)
	groupid = 0
	userid = 0
	groupids = []
	for apikey in APIKeys.objects.all():
		if apikey.value == request.headers['key']:
			groupid = apikey.intelgroup_id
			userid = apikey.user_id
	if groupid == 0 and userid == 0:
		return render(request, 'project/feeds.html', {'feeds':'This is invalid apikey.'})
	subid = IntelGroups.objects.filter(id=groupid).last().plan_id
	created_at = IntelGroups.objects.filter(id=groupid).last().created_at
	if subid == None:
		if datetime.now() > created_at.replace(tzinfo=None)+timedelta(days=30):
			return render(request, 'project/feeds.html', {'feeds': "Please select plan to perform this action."})
	else:
		planid = Subscription.objects.filter(djstripe_id=subid).last().plan_id
		productid = Plan.objects.filter(djstripe_id=planid).product_id
		current_period_end = Product.objects.filter(djstripe_id=productid).last().current_period_end
		history = PlanHistory.objects.filter(intelgroup_id=groupid).order_by('id').all()
		if Product.objects.filter(djstripe_id=productid).last().metadata['api_access'] == 'true':
			if datetime.now() > current_period_end.replace(tzinfo=None) and history[len(history)-2].end.replace(tzinfo=None):
				return render(request, 'project/feeds.html', {'feeds': 'Please select plan to perform this action.'})
		else:
			return render(request, 'project/feeds.html', {'feeds':'You are not allowed to access.'})

	if not 'uuids' in body:
		for role in UserIntelGroupRoles.objects.filter(user_id=userid).all():
			subid = IntelGroups.objects.filter(id=role.intelgroup_id).last().plan_id
			if subid != None:
				planid = Subscription.objects.filter(djstripe_id=subid).last().plan_id
				productid = Plan.objects.filter(djstripe_id=planid).last().product_id
				custom_feeds = Product.objects.filter(djstripe_id=productid).last().metadata['custom_feeds']
				current_period_end = Product.objects.filter(djstripe_id=productid).last().current_period_end
				if custom_feeds == 'true' and current_period_end.replace(tzinfo=None) > datetime.now():
					groupids.append(role.intelgroup_id)
	else:
		for group in IntelGroups.objects.filter(uniqueid__in=body['uuids']):
			if group.plan_id != None:
				planid = Subscription.objects.filter(djstripe_id=group.plan_id).last().plan_id
				productid = Plan.objects.filter(djstripe_id=planid).last().product_id
				custom_feeds = Product.objects.filter(djstripe_id=productid).last().metadata['custom_feeds']
				current_period_end = Product.objects.filter(djstripe_id=productid).last().current_period_end
				if custom_feeds == 'true' and current_period_end.replace(tzinfo=None) > datetime.now():
					groupids.append(group.id)
	if not 'confidence' in body:
		if not 'category' in body:
			if not 'tags' in body:
				if not 'created_at' in body:
					if not 'updated_at' in body:
						feeds = Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true').order_by('id').all()
					else:
						feeds = Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', updated_at__date=body['updated_at']).order_by('id').all()
				else:
					if not 'updated_at' in body:
						feeds = Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', created_at__date=body['created_at']).order_by('id').all()
					else:
						feeds = Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', updated_at__date=body['updated_at'], created_at__date=body['created_at']).order_by('id').all()
			else:
				if not 'created_at' in body:
					if not 'updated_at' in body:
						tags = body['tags'].split(',')
						temp = []
						feeds = []
						flag = True
						for tag in tags:
							temp = temp + list(Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', tags__contains=tag.strip()).order_by('id').all())
						for t in temp:
							for feed in feeds:
								if(feed.id == t.id):
									flag = False
							if flag:
								feeds.append(t)
					else:
						tags = body['tags'].split(',')
						temp = []
						feeds = []
						flag = True
						for tag in tags:
							temp = temp + list(Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', tags__contains=tag.strip(), updated_at__date=body['updated_at']).order_by('id').all())
						for t in temp:
							for feed in feeds:
								if(feed.id == t.id):
									flag = False
							if flag:
								feeds.append(t)
				else:
					if not 'updated_at' in body:
						tags = body['tags'].split(',')
						temp = []
						feeds = []
						flag = True
						for tag in tags:
							temp = temp + list(Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', tags__contains=tag.strip(), created_at__date=body['created_at']).order_by('id').all())
						for t in temp:
							for feed in feeds:
								if(feed.id == t.id):
									flag = False
							if flag:
								feeds.append(t)
					else:
						tags = body['tags'].split(',')
						temp = []
						feeds = []
						flag = True
						for tag in tags:
							temp = temp + list(Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', tags__contains=tag.strip(), created_at__date=body['created_at'], updated_at__date=body['updated_at']).order_by('id').all())
						for t in temp:
							for feed in feeds:
								if(feed.id == t.id):
									flag = False
							if flag:
								feeds.append(t)
		else:
			if not 'tags' in body:
				if not 'created_at' in body:
					if not 'updated_at' in body:
						feeds = Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', category=body['category']).order_by('id').all()
					else:
						feeds = Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', category=body['category'], updated_at__date=body['updated_at']).order_by('id').all()
				else:
					if not 'updated_at' in body:
						feeds = Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', category=body['category'], created_at__date=body['created_at']).order_by('id').all()
					else:
						feeds = Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', category=body['category'], created_at__date=body['created_at'], updated_at__date=body['updated_at']).order_by('id').all()
			else:
				if not 'created_at' in body:
					if not 'updated_at' in body:
						tags = body['tags'].split(',')
						temp = []
						feeds = []
						flag = True
						for tag in tags:
							temp = temp + list(Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', category=body['category'], tags__contains=tag.strip()).order_by('id').all())
						for t in temp:
							for feed in feeds:
								if(feed.id == t.id):
									flag = False
							if flag:
								feeds.append(t)
					else:
						tags = body['tags'].split(',')
						temp = []
						feeds = []
						flag = True
						for tag in tags:
							temp = temp + list(Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', category=body['category'], tags__contains=tag.strip(), updated_at__date=body['updated_at']).order_by('id').all())
						for t in temp:
							for feed in feeds:
								if(feed.id == t.id):
									flag = False
							if flag:
								feeds.append(t)
				else:
					if not 'updated_at' in body:
						tags = body['tags'].split(',')
						temp = []
						feeds = []
						flag = True
						for tag in tags:
							temp = temp + list(Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', category=body['category'], tags__contains=tag.strip(), created_at__date=body['created_at']).order_by('id').all())
						for t in temp:
							for feed in feeds:
								if(feed.id == t.id):
									flag = False
							if flag:
								feeds.append(t)
					else:
						tags = body['tags'].split(',')
						temp = []
						feeds = []
						flag = True
						for tag in tags:
							temp = temp + list(Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', category=body['category'], tags__contains=tag.strip(), created_at__date=body['created_at'], updated_at__date=body['updated_at']).order_by('id').all())
						for t in temp:
							for feed in feeds:
								if(feed.id == t.id):
									flag = False
							if flag:
								feeds.append(t)
	else:
		if not 'category' in body:
			if not 'tags' in body:
				if not 'created_at' in body:
					if not 'updated_at' in body:
						feeds = Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', confidence__gte=body['confidence']).order_by('id').all()
					else:
						feeds = Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', confidence__gte=body['confidence'], updated_at__date=body['updated_at']).order_by('id').all()
				else:
					if not 'updated_at' in body:
						feeds = Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', confidence__gte=body['confidence'], created_at__date=body['created_at']).order_by('id').all()
					else:
						feeds = Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', confidence__gte=body['confidence'], created_at__date=body['created_at'], updated_at__date=body['updated_at']).order_by('id').all()
			else:
				if not 'created_at' in body:
					if not 'updated_at' in body:
						tags = body['tags'].split(',')
						temp = []
						feeds = []
						flag = True
						for tag in tags:
							temp = temp + list(Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', confidence__gte=body['confidence'], tags__contains=tag.strip()).order_by('id').all())
						for t in temp:
							for feed in feeds:
								if(feed.id == t.id):
									flag = False
							if flag:
								feeds.append(t)
					else:
						tags = body['tags'].split(',')
						temp = []
						feeds = []
						flag = True
						for tag in tags:
							temp = temp + list(Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', confidence__gte=body['confidence'], updated_at__date=body['updated_at'], tags__contains=tag.strip()).order_by('id').all())
						for t in temp:
							for feed in feeds:
								if(feed.id == t.id):
									flag = False
							if flag:
								feeds.append(t)
				else:
					if not 'updated_at' in body:
						tags = body['tags'].split(',')
						temp = []
						feeds = []
						flag = True
						for tag in tags:
							temp = temp + list(Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', confidence__gte=body['confidence'], created_at__date=['created_at'], tags__contains=tag.strip()).order_by('id').all())
						for t in temp:
							for feed in feeds:
								if(feed.id == t.id):
									flag = False
							if flag:
								feeds.append(t)
					else:
						tags = body['tags'].split(',')
						temp = []
						feeds = []
						flag = True
						for tag in tags:
							temp = temp + list(Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', confidence__gte=body['confidence'], created_at__date=['created_at'], updated_at__date=['updated_at'], tags__contains=tag.strip()).order_by('id').all())
						for t in temp:
							for feed in feeds:
								if(feed.id == t.id):
									flag = False
							if flag:
								feeds.append(t)
		else:
			if not 'tags' in body:
				if not 'created_at' in body:
					if not 'updated_at' in body:
						feeds = Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', confidence__gte=body['confidence'], category=body['category']).order_by('id').all()
					else:
						feeds = Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', confidence__gte=body['confidence'], category=body['category'], updated_at__date=body['updated_at']).order_by('id').all()
				else:
					if not 'updated_at' in body:
						feeds = Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', confidence__gte=body['confidence'], category=body['category'], created_at__date=body['created_at']).order_by('id').all()
					else:
						feeds = Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', confidence__gte=body['confidence'], category=body['category'], created_at__date=body['created_at'], updated_at__date=body['updated_at']).order_by('id').all()
			else:
				if not 'created_at' in body:
					if not 'updated_at' in body:
						tags = body['tags'].split(',')
						temp = []
						feeds = []
						flag = True
						for tag in tags:
							temp = temp + list(Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', confidence__gte=body['confidence'], category=body['category'], tags__contains=tag.strip()).order_by('id').all())
						for t in temp:
							for feed in feeds:
								if(feed.id == t.id):
									flag = False
							if flag:
								feeds.append(t)
					else:
						tags = body['tags'].split(',')
						temp = []
						feeds = []
						flag = True
						for tag in tags:
							temp = temp + list(Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', confidence__gte=body['confidence'], category=body['category'], updated_at__date=body['updated_at'], tags__contains=tag.strip()).order_by('id').all())
						for t in temp:
							for feed in feeds:
								if(feed.id == t.id):
									flag = False
							if flag:
								feeds.append(t)
				else:
					if not 'updated_at' in body:
						tags = body['tags'].split(',')
						temp = []
						feeds = []
						flag = True
						for tag in tags:
							temp = temp + list(Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', confidence__gte=body['confidence'], category=body['category'], created_at__date=body['created_at'], tags__contains=tag.strip()).order_by('id').all())
						for t in temp:
							for feed in feeds:
								if(feed.id == t.id):
									flag = False
							if flag:
								feeds.append(t)
					else:
						tags = body['tags'].split(',')
						temp = []
						feeds = []
						flag = True
						for tag in tags:
							temp = temp + list(Feeds.objects.filter(intelgroup_id__in=groupids, manage_enabled='true', confidence__gte=body['confidence'], category=body['category'], created_at__date=body['created_at'], updated_at__date=body['updated_at'], tags__contains=tag.strip()).order_by('id').all())
						for t in temp:
							for feed in feeds:
								if(feed.id == t.id):
									flag = False
							if flag:
								feeds.append(t)
	
	feed_serializer = GroupCategoryFeedSerializer(feeds, many=True)
	return render(request, 'project/feeds.html', {'feeds':json.dumps(feed_serializer.data)})

@csrf_exempt
def apireports(request):
	body_unicode = request.body.decode('utf-8')
	body = json.loads(body_unicode)
	groupid = 0
	userid = 0
	tempgroupids = []
	groupids = []
	feedids = []
	for apikey in APIKeys.objects.all():
		if apikey.value == request.headers['key']:
			groupid = apikey.intelgroup_id
		userid = apikey.user_id
	if groupid == 0 and userid == 0:
		return render(request, 'project/reports.html', {'reports':'This is invalid apikey.'})
	subid = IntelGroups.objects.filter(id=groupid).last().plan_id
	created_at = IntelGroups.objects.filter(id=groupid).last().created_at
	if subid == None:
		if datetime.now() > created_at.replace(tzinfo=None)+timedelta(days=30):
			return render(request, 'project/reports.html', {'reports': "Please select plan to perform this action."})
	else:
		planid = Subscription.objects.filter(djstripe_id=subid).last().plan_id
		productid = Plan.objects.filter(djstripe_id=planid).product_id
		current_period_end = Product.objects.filter(djstripe_id=productid).last().current_period_end
		history = PlanHistory.objects.filter(intelgroup_id=groupid).order_by('id').all()
		if Product.objects.filter(djstripe_id=productid).last().metadata['api_access'] == 'true':
			if datetime.now() > current_period_end.replace(tzinfo=None) and history[len(history)-2].end.replace(tzinfo=None):
				return render(request, 'project/reports.html', {'reports': 'Please select plan to perform this action.'})
		else:
			return render(request, 'project/reports.html', {'reports':'You are not allowed to access.'})
	if not 'attributes' in body:
		if not 'uuids' in body:
			for role in UserIntelGroupRoles.objects.filter(user_id=userid):
				tempgroupids.append(role.intelgroup_id)
		else:
			for group in IntelGroups.objects.filter(uniqueid__in=body['uuids']):
				tempgroupids.append(group.id)
	else:
		if not 'uuids' in body:
			attributelist = list(body['attributes'])
			tempids = []
			for api_attribute in attributelist:
				for globalattribute in GlobalAttributes.objects.filter(api_attribute=api_attribute.strip(), words_matched__contains=body['attributes'][api_attribute].strip()).order_by('id').all():
					tempids.append(globalattribute.intelgroup_id)
			for tempid in tempids:
				flag = True
				for groupid in tempgroupids:
					if tempid == groupid:
						flag = False
				if flag:
					tempgroupids.append(tempid)
		else:
			attributelist = list(body['attributes'])
			apitempids = []
			uuidtempids = []
			for api_attribute in attributelist:
				for globalattribute in GlobalAttributes.objects.filter(api_attribute=api_attribute.strip(), words_matched__contains=body['attributes'][api_attribute].strip()).order_by('id').all():
					apitempids.append(globalattribute.intelgroup_id)
			for group in IntelGroups.objects.filter(uniqueid__in=body['uuids']).all():
				uuidtempids.append(group.id)
			for uuidtempid in uuidtempids:
				for apitempid in apitempids:
					if uuidtempid == apitempid:
						tempgroupids.append(uuidtempid)
	for group in IntelGroups.objects.filter(id__in=tempgroupids).all():
		if group.plan_id != None:
			planid = Subscription.objects.filter(djstripe_id=group.plan_id).last().plan_id
			productid = Plan.objects.filter(djstripe_id=planid).last().product_id
			custom_feeds = Product.objects.filter(djstripe_id=productid).last().metadata['custom_feeds']
			current_period_end = Product.objects.filter(djstripe_id=productid).last().current_period_end
			if custom_feeds == 'true' and current_period_end.replace(tzinfo=None) > datetime.now():
				groupids.append(group.id)

	if not 'feedids' in body:
		if not 'created_at' in body:
			if not 'updated_at' in body:
				for feed in Feeds.objects.filter(intelgroup_id__in=groupids):
					feedids.append(feed.id)
			else:
				for feed in Feeds.objects.filter(intelgroup_id__in=groupids, updated_at__date=body['updated_at']):
					feedids.append(feed.id)
		else:
			if not 'updated_at' in body:
				for feed in Feeds.objects.filter(intelgroup_id__in=groupids, created_at__date=body['created_at']):
					feedids.append(feed.id)
			else:
				for feed in Feeds.objects.filter(intelgroup_id__in=groupids, created_at__date=body['created_at'], updated_at__date=body['updated_at']):
					feedids.append(feed.id)
	else:
		if not 'created_at' in body:
			if not 'updated_at' in body:
				for feed in Feeds.objects.filter(intelgroup_id__in=groupids, uniqueid__in=feedids):
					feedids.append(feed.id)
			else:
				for feed in Feeds.objects.filter(intelgroup_id__in=groupids, uniqueid__in=feedids, updated_at__date=body['updated_at']):
					feedids.append(feed.id)
		else:
			if not 'updated_at' in body:
				for feed in Feeds.objects.filter(intelgroup_id__in=groupids, uniqueid__in=feedids, created_at__date=body['created_at']):
						feedids.append(feed.id)
			else:
				for feed in Feeds.objects.filter(intelgroup_id__in=groupids, uniqueid__in=feedids, created_at__date=body['created_at'], updated_at__date=body['created_at']):
					feedids.append(feed.id)
	if not 'indicators' in body:
		feeditems = FeedItems.objects.filter(feed_id__in=feedids).order_by('id').all()
	else:
		tempitemids = []
		itemids = []
		for feeditem in FeedItems.objects.filter(feed_id__in=feedids).order_by('id').all():
			tempitemids.append(feeditem.id)
		indicators = Indicators.objects.filter(feeditem_id__in=tempitemids).order_by('id').all()
		serializer = IndicatorGlobalSerializer(indicators, many=True)
		for s in serializer.data:
			for indicator in body['indicators']:
				if s['globalindicator']['value_api'] == indicator:
					itemids.append(s['feeditem_id'])
		newitemids = []
		for itemid in itemids:
			flag = True
			for newitemid in newitemids:
				if newitemid == itemid:
					flag = False
			if flag:
				newitemids.append(itemid)
		feeditems = FeedItems.objects.filter(id__in=newitemids).order_by('id').all()

	item_serializer = FeedItemSerializer(feeditems, many=True)
	return render(request, 'project/reports.html', {'reports':json.dumps(item_serializer.data)})

@csrf_exempt
def apigroups(request):
	groupid = 0
	userid = 0
	for apikey in APIKeys.objects.all():
		if apikey.value == request.headers['key']:
			groupid = apikey.intelgroup_id
			userid = apikey.user_id
	if groupid == 0 and userid == 0:
		return render(request, 'project/intel_groups.html', {'feeds':'This is invalid apikey.'})
	groups = UserIntelGroupRoles.objects.filter(intelgroup_id=groupid, user_id=userid).all()
	subid = groups[0].plan_id
	created_at = groups[0].created_at
	if subid == None:
		if datetime.now() > created_at.replace(tzinfo=None)+timedelta(days=30):
			return render(request, 'project/intel_groups.html', {'groups':"Please select plan to perform this action."})
	else:
		planid = Subscription.objects.filter(djstripe_id=subid).last().plan_id
		productid = Plan.objects.filter(djstripe_id=planid).product_id
		current_period_end = Product.objects.filter(djstripe_id=productid).last().current_period_end
		history = PlanHistory.objects.filter(intelgroup_id=groupid).order_by('id').all()
		if Product.objects.filter(djstripe_id=productid).last().metadata['api_access'] == 'true':
			if datetime.now() > current_period_end.replace(tzinfo=None) and history[len(history)-2].end.replace(tzinfo=None):
				return render(request, 'project/intel_groups.html', {'groups': 'Please select plan to perform this action.'})
		else:
			return render(request, 'project/intel_groups.html', {'groups':'You are not allowed to access.'})
	group_serializer = GroupRoleSerializer(groups[0])
	return render(request, 'project/intel_groups.html', {'groups':json.dumps(group_serializer.data)})

@api_view(['POST'])
@permission_classes([AllowAny])
def webhook(request):
	endpoint_secret = os.environ.get('DJSTRIPE_WEBHOOK_SECRET')
	payload = request.body
	sig_header = request.META['HTTP_STRIPE_SIGNATURE']
	event = None
	try:
		event = stripe.Webhook.construct_event(
		payload, sig_header, endpoint_secret
		)
	except ValueError as e:
		# Invalid payload
		return HttpResponse(status=400)
	except stripe.error.SignatureVerificationError as e:
		# Invalid signature
		return HttpResponse(status=400)
	if event.type == 'product.created':
		product = event.data.object
		new_product = Product.objects.create(active=product['active'], attributes=product['attributes'],caption="", created=datetime.fromtimestamp(product['created']), deactivate_on="", description=product['description'], \
			id=product['id'], images=product['images'], livemode=product['livemode'], metadata=product['metadata'], name=product['name'], package_dimensions="", \
				statement_descriptor="", type=product['type'], unit_label="", url="")
		
	elif event.type == 'plan.created':
		plan = event.data.object
		Plan.objects.create(active=plan['active'], aggregate_usage="", amount=plan['amount'], billing_scheme=plan['billing_scheme'], created=datetime.fromtimestamp(plan['created']), \
			currency=plan['currency'], id=plan['id'], interval=plan['interval'], interval_count=plan['interval_count'], livemode=plan['livemode'], metadata=plan['metadata'], \
				nickname="", product_id=Product.objects.order_by('id').last().djstripe_id, tiers_mode="", transform_usage="", \
					trial_period_days=0, usage_type=plan['usage_type'])
	return Response({'message': 'ok'})


@swagger_auto_schema(methods=['get'], responses={200: UserSerializer})
@api_view(['GET'])
def account(request):
	profile = CustomUser.objects.filter(id=request.user.id).all()[0]
	serializer = UserSerializer(profile)
	profile_data = serializer.data
	intelgroups = UserIntelGroupRoles.objects.order_by('id').filter(user_id=request.user.id).all()
	intelgroup_data = []
	for intelgroup in intelgroups:
		serializer = RoleGroupSerializer(intelgroup)
		intelgroup_data.append(serializer.data)
	apikeys = APIKeys.objects.order_by('id').filter(user_id=request.user.id).all()
	apikey_data = []
	for apikey in apikeys:
		serializer = GroupAPIkeySerializer(apikey)
		apikey_data.append(serializer.data)
	webhooks = WebHooks.objects.order_by('id').filter(user_id=request.user.id).all()
	webhook_data = []
	for webhook in webhooks:
		serializer = GroupWebHookSerializer(webhook)
		webhook_data.append(serializer.data)
	
	return Response({'profile':profile_data, 'intelgroups':intelgroup_data, 'apikeys':apikey_data, 'webhooks':webhook_data});

@swagger_auto_schema(methods=['post'], request_body=ChangeEmailSerializer, responses={201: UserSerializer})
@api_view(['POST'])
def emailchange(request):
	users = CustomUser.objects.filter(email=request.data['email']).all()
	if len(users) > 1:
		return Response({'isExist':True})
	elif len(users) == 1:
		if users[0].email != request.user.email:
			return Response({'isExist': True})
	CustomUser.objects.filter(id=request.data['id']).update(email=request.data['email'])
	serializer = UserSerializer(CustomUser.objects.filter(id=request.data['id']).all()[0])
	return Response(serializer.data)

@swagger_auto_schema(methods=['post'], request_body=APIKeyCreateSerializer, responses={201: GroupAPIkeySerializer})
@swagger_auto_schema(methods=['delete'], request_body=IDSerializer, responses={204: GroupAPIkeySerializer})
@api_view(['POST', 'DELETE'])
def apikeys(request):
	if request.method == 'POST':
		apikeys = []
		key = secrets.token_urlsafe(16)
		APIKeys.objects.create(name=request.data['name'], intelgroup_id=request.data['intelgroup_id'], value=key, user_id=request.user.id)
		for apikey in APIKeys.objects.filter(user_id=request.user.id).all():
			serializer = GroupAPIkeySerializer(apikey)
			apikeys.append(serializer.data)
			
		return Response(apikeys)
	if request.method == 'DELETE':
		APIKeys.objects.filter(id=request.data['id']).delete()
		apikeys = APIKeys.objects.filter(user_id=request.user.id).all()
		apikey_serializer = GroupAPIkeySerializer(apikeys, many=True)
		return Response(apikey_serializer.data)

@swagger_auto_schema(methods=['post'], request_body=WebhookCreateSerializer, responses={201: GroupWebHookSerializer})
@swagger_auto_schema(methods=['put'], request_body=WebhookUpdateSerializer, responses={200: GroupWebHookSerializer})
@swagger_auto_schema(methods=['delete'], request_body=IDSerializer, responses={204: GroupWebHookSerializer})
@api_view(['POST', 'PUT', 'DELETE'])
def webhooks(request):
	if request.method == 'POST':
		WebHooks.objects.create(endpoint=request.data['endpoint'], description=request.data['description'], intelgroup_id=request.data['intelgroup_id'], user_id=request.user.id)
		webhooks = []
		for webhook in WebHooks.objects.filter(user_id=request.user.id).all():
			serializer = GroupWebHookSerializer(webhook)
			webhooks.append(serializer.data)
		return Response(webhooks)
	elif request.method == 'PUT':
		WebHooks.objects.filter(id=request.data['id']).update(endpoint=request.data['endpoint'], description=request.data['description'], intelgroup_id=request.data['intelgroup_id'], user_id=request.user.id, isenable=request.data['isenable'])
		webhooks = []
		for webhook in WebHooks.objects.filter(user_id=request.user.id).all():
			serializer = GroupWebHookSerializer(webhook)
			webhooks.append(serializer.data)
		return Response(webhooks)
	elif request.method == 'DELETE':
		WebHooks.objects.filter(id=request.data['id']).delete()
		webhooks = []
		for webhook in WebHooks.objects.filter(user_id=request.user.id).all():
			serializer = GroupWebHookSerializer(webhook)
			webhooks.append(serializer.data)
		return Response(webhooks)

@swagger_auto_schema(methods=['get'], responses={201: FeedCategorySerializer})
@api_view(['GET'])
def reports(request, id):
	feeds = []
	groupids = []
	feedids = []
	myfeedids = []
	feedchannels = []
	feeditems =[]
	itemids = []
	for role in UserIntelGroupRoles.objects.order_by('id').filter(user_id=request.user.id).all():
		groupids.append(role.intelgroup_id)
	for feed in Feeds.objects.order_by('id').filter(intelgroup_id__in=groupids, manage_enabled='true').all():
		serializer = FeedCategorySerializer(feed)
		feeds.append(serializer.data)
		feedids.append(Feeds.objects.filter(uniqueid=feed.uniqueid).order_by('id').first().id)
	for channel in FeedChannels.objects.filter(feed_id__in=feedids).order_by('id').all():
		serializer = FeedChannelSerializer(channel)
		feedchannels.append(serializer.data)
	for item in FeedItems.objects.filter(feed_id__in=feedids).order_by('id').all():
		serializer = FeedItemSerializer(item)
		feeditems.append(serializer.data)
		itemids.append(item.id)
	indicators = Indicators.objects.filter(feeditem_id__in=itemids, enabled='Enable').order_by('id').all()
	indicator_serializer = ItemIndicatorSerializer(indicators, many=True)
	extractions = Attributes.objects.filter(intelgroup_id__in=groupids).filter(enabled='Enable').order_by('id').all()
	extraction_serializer = UserGroupAttributeSerializer(extractions, many=True)
	categories = Categories.objects.order_by('id').all()
	category_serializer = CategorySerializer(categories, many=True)
	tags = Tags.objects.filter(Q(isglobal=True) | Q(user_id=request.user.id)).order_by('id').all()
	tag_serializer = TagSerializer(tags, many=True)
	globalindicators = GlobalIndicators.objects.order_by('id').all()
	global_serializer = GlobalIndicatorSerializer(globalindicators, many=True)
	feed_ids = []
	for feed in Feeds.objects.filter(intelgroup_id=id, manage_enabled='true').order_by('id').all():
		feed_ids.append(feed.id)
	reports = ItemFeedGroupReportSerializer(IntelReports.objects.filter(feed_id__in=feed_ids).order_by('id').all(), many=True)


	return Response({'feeds':feeds, 'feedchannels':feedchannels, 'feeditems':feeditems, 'indicators':indicator_serializer.data, 'extractions':extraction_serializer.data, 'categories':category_serializer.data, 'tags':tag_serializer.data, 'globalindicators':global_serializer.data, 'reports':reports.data})

@swagger_auto_schema(methods=['post'], request_body=SearchReportSerializer, responses={201: FeedCategorySerializer})
@api_view(['POST'])
def searchreports(request):
	feeds = []
	groupids = []
	feedids = []
	myfeedids = []
	feedchannels = []
	feeditems =[]
	itemids = []

	if(request.data['classification'] != '0'):
		temp = []
		for role in UserIntelGroupRoles.objects.order_by('id').filter(user_id=request.user.id).all():
			temp.append(role.intelgroup_id)
		word = Attributes.objects.filter(id=request.data['classification']).values()[0]['words_matched']
		for extraction in Attributes.objects.filter(intelgroup_id__in=temp).filter(words_matched__contains=word):
			groupids.append(extraction.intelgroup_id)
	else:
		for role in UserIntelGroupRoles.objects.order_by('id').filter(user_id=request.user.id).all():
			groupids.append(role.intelgroup_id)
	if(request.data['category'] == '0'):
		if(request.data['tag'] == '0'):
			if(request.data['confidence'] == '0'):
				if(request.data['feedname'] == '0'):
					for feed in Feeds.objects.order_by('id').filter(intelgroup_id__in=groupids, manage_enabled='true').all():
						serializer = FeedCategorySerializer(feed)
						feeds.append(serializer.data)
						feedids.append(Feeds.objects.filter(uniqueid=feed.uniqueid).order_by('id').first().id)
				else:
					for feed in Feeds.objects.order_by('id').filter(intelgroup_id__in=groupids, manage_enabled='true').filter(id=request.data['feedname']).all():
						serializer = FeedCategorySerializer(feed)
						feeds.append(serializer.data)
						feedids.append(Feeds.objects.filter(uniqueid=feed.uniqueid).order_by('id').first().id)
			else:
				if(request.data['feedname'] == '0'):
					for feed in Feeds.objects.order_by('id').filter(intelgroup_id__in=groupids, manage_enabled='true').filter(confidence__gte=request.data['confidence']).all():
						serializer = FeedCategorySerializer(feed)
						feeds.append(serializer.data)
						feedids.append(Feeds.objects.filter(uniqueid=feed.uniqueid).order_by('id').first().id)
				else:
					for feed in Feeds.objects.order_by('id').filter(intelgroup_id__in=groupids, manage_enabled='true').filter(id=request.data['feedname']).filter(confidence__gte=request.data['confidence']).all():
						serializer = FeedCategorySerializer(feed)
						feeds.append(serializer.data)
						feedids.append(Feeds.objects.filter(uniqueid=feed.uniqueid).order_by('id').first().id)
		else:
			if(request.data['confidence'] == '0'):
				if(request.data['feedname'] == '0'):
					for feed in Feeds.objects.order_by('id').filter(intelgroup_id__in=groupids, manage_enabled='true').filter(tags__contains=request.data['tag']).all():
						serializer = FeedCategorySerializer(feed)
						feeds.append(serializer.data)
						feedids.append(Feeds.objects.filter(uniqueid=feed.uniqueid).order_by('id').first().id)
				else:
					for feed in Feeds.objects.order_by('id').filter(intelgroup_id__in=groupids, manage_enabled='true').filter(tags__contains=request.data['tag']).filter(id=request.data['feedname']).all():
						serializer = FeedCategorySerializer(feed)
						feeds.append(serializer.data)
						feedids.append(Feeds.objects.filter(uniqueid=feed.uniqueid).order_by('id').first().id)
			else:
				if(request.data['feedname'] == '0'):
					for feed in Feeds.objects.order_by('id').filter(intelgroup_id__in=groupids, manage_enabled='true').filter(tags__contains=request.data['tag']).filter(confidence__gte=request.data['confidence']).all():
						serializer = FeedCategorySerializer(feed)
						feeds.append(serializer.data)
						feedids.append(Feeds.objects.filter(uniqueid=feed.uniqueid).order_by('id').first().id)
				else:
					for feed in Feeds.objects.order_by('id').filter(intelgroup_id__in=groupids, manage_enabled='true').filter(tags__contains=request.data['tag']).filter(confidence__gte=request.data['confidence']).filter(id=request.data['feedname']).all():
						serializer = FeedCategorySerializer(feed)
						feeds.append(serializer.data)
						feedids.append(Feeds.objects.filter(uniqueid=feed.uniqueid).order_by('id').first().id)
	else:
		if(request.data['tag'] == '0'):
			if(request.data['confidence'] == '0'):
				if(request.data['feedname'] == '0'):
					for feed in Feeds.objects.order_by('id').filter(intelgroup_id__in=groupids, manage_enabled='true').filter(category_id=request.data['category']).all():
						serializer = FeedCategorySerializer(feed)
						feeds.append(serializer.data)
						feedids.append(Feeds.objects.filter(uniqueid=feed.uniqueid).order_by('id').first().id)
				else:
					for feed in Feeds.objects.order_by('id').filter(intelgroup_id__in=groupids, manage_enabled='true').filter(category_id=request.data['category']).filter(id=request.data['feedname']).all():
						serializer = FeedCategorySerializer(feed)
						feeds.append(serializer.data)
						feedids.append(Feeds.objects.filter(uniqueid=feed.uniqueid).order_by('id').first().id)
			else:
				if(request.data['feedname'] == '0'):
					for feed in Feeds.objects.order_by('id').filter(intelgroup_id__in=groupids, manage_enabled='true').filter(category_id=request.data['category']).filter(confidence__gte=request.data['confidence']).all():
						serializer = FeedCategorySerializer(feed)
						feeds.append(serializer.data)
						feedids.append(Feeds.objects.filter(uniqueid=feed.uniqueid).order_by('id').first().id)
				else:
					for feed in Feeds.objects.order_by('id').filter(intelgroup_id__in=groupids, manage_enabled='true').filter(category_id=request.data['category']).filter(confidence__gte=request.data['confidence']).filter(id=request.data['feedname']).all():
						serializer = FeedCategorySerializer(feed)
						feeds.append(serializer.data)
						feedids.append(Feeds.objects.filter(uniqueid=feed.uniqueid).order_by('id').first().id)
		else:
			if(request.data['confidence'] == '0'):
				if(request.data['feedname'] == '0'):
					for feed in Feeds.objects.order_by('id').filter(intelgroup_id__in=groupids, manage_enabled='true').filter(category_id=request.data['category']).filter(tags__contains=request.data['tag']).all():
						serializer = FeedCategorySerializer(feed)
						feeds.append(serializer.data)
						feedids.append(Feeds.objects.filter(uniqueid=feed.uniqueid).order_by('id').first().id)
				else:
					for feed in Feeds.objects.order_by('id').filter(intelgroup_id__in=groupids, manage_enabled='true').filter(category_id=request.data['category']).filter(tags__contains=request.data['tag']).filter(id=request.data['feedname']).all():
						serializer = FeedCategorySerializer(feed)
						feeds.append(serializer.data)
						feedids.append(Feeds.objects.filter(uniqueid=feed.uniqueid).order_by('id').first().id)
			else:
				if(request.data['feedname'] == '0'):
					for feed in Feeds.objects.order_by('id').filter(intelgroup_id__in=groupids, manage_enabled='true').filter(category_id=request.data['category']).filter(tags__contains=request.data['tag']).filter(confidence__gte=request.data['confidence']).all():
						serializer = FeedCategorySerializer(feed)
						feeds.append(serializer.data)
						feedids.append(Feeds.objects.filter(uniqueid=feed.uniqueid).order_by('id').first().id)
				else:
					for feed in Feeds.objects.order_by('id').filter(intelgroup_id__in=groupids, manage_enabled='true').filter(category_id=request.data['category']).filter(tags__contains=request.data['tag']).filter(confidence__gte=request.data['confidence']).filter(id=request.data['feedname']).all():
						serializer = FeedCategorySerializer(feed)
						feeds.append(serializer.data)
						feedids.append(Feeds.objects.filter(uniqueid=feed.uniqueid).order_by('id').first().id)

	for channel in FeedChannels.objects.filter(feed_id__in=feedids).order_by('id').all():
		serializer = FeedChannelSerializer(channel)
		feedchannels.append(serializer.data)
	for item in FeedItems.objects.filter(feed_id__in=feedids).order_by('id').all():
		serializer = FeedItemSerializer(item)
		feeditems.append(serializer.data)
		itemids.append(item.id)
	indicator_feeditem_ids = []
	indicator_feed_ids = []
	search_feeds = []
	search_feedchannels = []
	search_feeditems = []
	if(request.data['indicator'] != '0'):
		for indicator in Indicators.objects.filter(feeditem_id__in=itemids, enabled='Enable').filter(globalindicator_id=request.data['indicator']).order_by('id').all():
			indicator_feeditem_ids.append(indicator.feeditem_id)
		for feeditem in FeedItems.objects.filter(id__in=indicator_feeditem_ids).order_by('id').all():
			flag = False
			for indicator_feed_id in indicator_feed_ids:
				if feeditem.feed_id == indicator_feed_id:
					flag = True
			if not flag:
				indicator_feed_ids.append(feeditem.feed_id)
		for indicator_feed_id in indicator_feed_ids:
			for feed in feeds:
				if feed['id'] == indicator_feed_id:
					search_feeds.append(feed)
		for channel in FeedChannels.objects.filter(feed_id__in=indicator_feed_ids).order_by('id').all():
			serializer = FeedChannelSerializer(channel)
			search_feedchannels.append(serializer.data)
		for item in FeedItems.objects.filter(id__in=indicator_feeditem_ids).order_by('id').all():
			serializer = FeedItemSerializer(item)
			search_feeditems.append(serializer.data)
	else:
		search_feeds = feeds
		search_feedchannels = feedchannels
		search_feeditems = feeditems
	search_serializer = FeedCategorySerializer(search_feeds, many=True)
	indicators = Indicators.objects.filter(feeditem_id__in=itemids, enabled='Enable').order_by('id').all()
	indicator_serializer = ItemIndicatorSerializer(indicators, many=True)
	extractions = Attributes.objects.filter(intelgroup_id__in=groupids).filter(enabled='Enable').order_by('id').all()
	extraction_serializer = UserGroupAttributeSerializer(extractions, many=True)
	categories = Categories.objects.order_by('id').all()
	category_serializer = CategorySerializer(categories, many=True)
	tags = Tags.objects.filter(Q(isglobal=True) | Q(user_id=request.user.id)).order_by('id').all()
	tag_serializer = TagSerializer(tags, many=True)
	globalindicators = GlobalIndicators.objects.order_by('id').all()
	global_serializer = GlobalIndicatorSerializer(globalindicators, many=True)

	return Response({'feeds':search_serializer.data, 'feedchannels':search_feedchannels, 'feeditems':search_feeditems, 'indicators':indicator_serializer.data, 'extractions':extraction_serializer.data, 'categories':category_serializer.data, 'tags':tag_serializer.data, 'globalindicators':global_serializer.data})


@api_view(['POST'])
def pullfeed(request):
	ftr = "http://ftr-premium.fivefilters.org/"
	encode = urllib.parse.quote_plus(request.data['url'])
	key = urllib.parse.quote_plus("KSF8GH22GZRKA8")
	req = urllib.request.Request(ftr+"makefulltextfeed.php?url="+encode+"&key="+key)
	contents = urllib.request.urlopen(req).read()
	return Response({'fulltext':xmltodict.parse(contents)})


@swagger_auto_schema(methods=['post'], request_body=FeedCreateSerializer, responses={201: FeedCategorySerializer})
@swagger_auto_schema(methods=['put'], request_body=FeedUpdateSerializer, responses={200: FeedCategorySerializer})
@api_view(['POST', 'PUT'])
def feeds(request):
	if request.method == 'POST':
		data=request.data
		tags = data['tags'].split(',')
		groupid= request.data['intelgroup_id']
		isUrlExist = False
		isEqualGroup = False
		for feed in Feeds.objects.all():
			if(data['url'] in feed.url):
				isUrlExist = True
				if feed.intelgroup_id == int(groupid):
					isEqualGroup = True
					Feeds.objects.filter(id=feed.id).update(url=data['url'], name=data['name'], description=data['description'], category_id=data['category'], tags=data['tags'], manage_enabled='false', intelgroup_id=groupid, confidence=data['confidence'], updated_at=datetime.now(), type=data['type'])
					for tag in tags:
						flag = False
						for existingtag in Tags.objects.all():
							if tag.strip() == existingtag.name:
								flag = True
						if not flag:
							if request.user.is_staff:
								Tags.objects.create(name=tag.strip(), isglobal=True, user_id=request.user.id)
							else:
								Tags.objects.create(name=tag.strip(), isglobal=False, user_id=request.user.id)
		if isUrlExist and not isEqualGroup:
			subid = IntelGroups.objects.filter(id=groupid).last().plan_id
			max_feeds = 0
			if not subid == None:
				planid = Subscription.objects.filter(djstripe_id=subid).last().plan_id
				productid = Plan.objects.filter(djstripe_id=planid).last().product_id
				max_feeds = Product.objects.filter(djstripe_id=productid).last().metadata['max_feeds']
			feeds = Feeds.objects.filter(intelgroup_id=groupid).all()
			if len(feeds) > int(max_feeds):
				return Response({'message':True})
			Feeds.objects.create(uniqueid=Feeds.objects.filter(url=data['url']).order_by('id').first().uniqueid, url=data['url'], name=data['name'], description=data['description'], category_id=data['category'], tags=data['tags'], manage_enabled='false', intelgroup_id=groupid, confidence=data['confidence'], type=data['type'])
			for item in FeedItems.objects.filter(feed_id=Feeds.objects.filter(url=data['url']).order_by('id').first().id).order_by('id').all():
				IntelReports.objects.create(feed_id=Feeds.objects.last().id, intelgroup_id=groupid, feeditem_id=item.id)
			for tag in tags:
				flag = False
				for existingtag in Tags.objects.all():
					if tag.strip() == existingtag.name:
						flag = True
				if not flag:
					if request.user.is_staff:
						Tags.objects.create(name=tag.strip(), isglobal=True, user_id=request.user.id)
					else:
						Tags.objects.create(name=tag.strip(), isglobal=False, user_id=request.user.id)
			isUrlExist = True

		if not isUrlExist:
			subid = IntelGroups.objects.filter(id=groupid).last().plan_id
			max_feeds = 0
			if not subid == None:
				planid = Subscription.objects.filter(djstripe_id=subid).last().plan_id
				productid = Plan.objects.filter(djstripe_id=planid).last().product_id
				max_feeds = Product.objects.filter(djstripe_id=productid).last().metadata['max_feeds']
			feeds = Feeds.objects.filter(intelgroup_id=groupid).all()
			if len(feeds) > int(max_feeds):
				return Response({'message':True})
			Feeds.objects.create(url=data['url'], name=data['name'], description=data['description'], category_id=data['category'], tags=data['tags'], manage_enabled='false', intelgroup_id=groupid, confidence=data['confidence'], type=data['type'])
			for tag in tags:
				flag = False
				for existingtag in Tags.objects.all():
					if tag.strip() == existingtag.name:
						flag = True
				if not flag:
					if request.user.is_staff:
						Tags.objects.create(name=tag.strip(), isglobal=True, user_id=request.user.id)
					else:
						Tags.objects.create(name=tag.strip(), isglobal=False, user_id=request.user.id)
			ftr = "http://ftr-premium.fivefilters.org/"
			encode = urllib.parse.quote_plus(data['url'])
			key = urllib.parse.quote_plus("KSF8GH22GZRKA8")
			req = urllib.request.Request(ftr+"makefulltextfeed.php?url="+encode+"&key="+key)
			contents = urllib.request.urlopen(req).read()
			FeedChannels.objects.create(feed_id=Feeds.objects.last().id)
			for item in xmltodict.parse(contents)['rss']['channel']:
				if(item == 'title'):
					FeedChannels.objects.filter(id=FeedChannels.objects.last().id).update(title=xmltodict.parse(contents)['rss']['channel'][item])
				elif(item == 'link'):
					FeedChannels.objects.filter(id=FeedChannels.objects.last().id).update(link=xmltodict.parse(contents)['rss']['channel'][item])
				elif(item == 'description'):
					FeedChannels.objects.filter(id=FeedChannels.objects.last().id).update(description=xmltodict.parse(contents)['rss']['channel'][item])
				elif(item == 'language'):
					FeedChannels.objects.filter(id=FeedChannels.objects.last().id).update(language=xmltodict.parse(contents)['rss']['channel'][item])
				elif(item == 'copyright'):
					FeedChannels.objects.filter(id=FeedChannels.objects.last().id).update(copyright=xmltodict.parse(contents)['rss']['channel'][item])
				elif(item == 'managingeditor'):
					FeedChannels.objects.filter(id=FeedChannels.objects.last().id).update(managingeditor=xmltodict.parse(contents)['rss']['channel'][item])
				elif(item == 'webmaster'):
					FeedChannels.objects.filter(id=FeedChannels.objects.last().id).update(webmaster=xmltodict.parse(contents)['rss']['channel'][item])
				elif(item == 'pubdate'):
					FeedChannels.objects.filter(id=FeedChannels.objects.last().id).update(pubdate=xmltodict.parse(contents)['rss']['channel'][item])
				elif(item == 'category'):
					FeedChannels.objects.filter(id=FeedChannels.objects.last().id).update(category=xmltodict.parse(contents)['rss']['channel'][item])
				elif(item == 'lastbuilddate'):
					FeedChannels.objects.filter(id=FeedChannels.objects.last().id).update(lastbuilddate=xmltodict.parse(contents)['rss']['channel'][item])
				elif(item == 'generator'):
					FeedChannels.objects.filter(id=FeedChannels.objects.last().id).update(generator=xmltodict.parse(contents)['rss']['channel'][item])
				elif(item == 'docs'):
					FeedChannels.objects.filter(id=FeedChannels.objects.last().id).update(docs=xmltodict.parse(contents)['rss']['channel'][item])
				elif(item == 'cloud'):
					FeedChannels.objects.filter(id=FeedChannels.objects.last().id).update(cloud=xmltodict.parse(contents)['rss']['channel'][item])
				elif(item == 'ttl'):
					FeedChannels.objects.filter(id=FeedChannels.objects.last().id).update(ttl=xmltodict.parse(contents)['rss']['channel'][item])
				elif(item == 'image'):
					FeedChannels.objects.filter(id=FeedChannels.objects.last().id).update(image=xmltodict.parse(contents)['rss']['channel'][item])
				elif(item == 'textinput'):
					FeedChannels.objects.filter(id=FeedChannels.objects.last().id).update(textinput=xmltodict.parse(contents)['rss']['channel'][item])
				elif(item == 'skiphours'):
					FeedChannels.objects.filter(id=FeedChannels.objects.last().id).update(skiphours=xmltodict.parse(contents)['rss']['channel'][item])
				elif(item == 'skipdays'):
					FeedChannels.objects.filter(id=FeedChannels.objects.last().id).update(skipdays=xmltodict.parse(contents)['rss']['channel'][item])
			
			if type(xmltodict.parse(contents)['rss']['channel']['item']) is not list:
				FeedItems.objects.create(feed_id=Feeds.objects.last().id)
				IntelReports.objects.create(feeditem_id=FeedItems.objects.last().id, feed_id=Feeds.objects.last().id, intelgroup_id=groupid)
				for item in xmltodict.parse(contents)['rss']['channel']['item']:
					if(item == 'title'):
						FeedItems.objects.filter(id=FeedItems.objects.last().id).update(title=xmltodict.parse(contents)['rss']['channel']['item'][item])
					elif(item == 'link'):
						FeedItems.objects.filter(id=FeedItems.objects.last().id).update(link=xmltodict.parse(contents)['rss']['channel']['item'][item])
					elif(item == 'description'):
						FeedItems.objects.filter(id=FeedItems.objects.last().id).update(description=xmltodict.parse(contents)['rss']['channel']['item'][item])
						text = json.dumps(xmltodict.parse(contents)['rss']['channel']['item'][item])
						results = extract.extract_observables(text)
						for result in results:
							if result == 'ipv4addr' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'ipv4cidr' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'ipv4range' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'ipv6addr' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'ipv6cidr' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'ipv6range' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'md5' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'sha1' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'sha256' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'ssdeep' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'fqdn' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'url' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'useragent' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'email' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'filename' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'filepath' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'regkey' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'asn' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'asnown' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'country' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'isp' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'cve' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'malware' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'attacktype' and len(results[result])>0:
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
					elif(item == 'author'):
						FeedItems.objects.filter(id=FeedItems.objects.last().id).update(author=xmltodict.parse(contents)['rss']['channel']['item'][item])
					elif(item == 'category'):
						FeedItems.objects.filter(id=FeedItems.objects.last().id).update(category=xmltodict.parse(contents)['rss']['channel']['item'][item])
					elif(item == 'comments'):
						FeedItems.objects.filter(id=FeedItems.objects.last().id).update(comments=xmltodict.parse(contents)['rss']['channel']['item'][item])
					elif(item == 'enclosure'):
						FeedItems.objects.filter(id=FeedItems.objects.last().id).update(enclosure=xmltodict.parse(contents)['rss']['channel']['item'][item])
					elif(item == 'guid'):
						FeedItems.objects.filter(id=FeedItems.objects.last().id).update(guid=xmltodict.parse(contents)['rss']['channel']['item'][item])
					elif(item == 'pubdate'):
						FeedItems.objects.filter(id=FeedItems.objects.last().id).update(pubdate=xmltodict.parse(contents)['rss']['channel']['item'][item])
					elif(item == 'source'):
						FeedItems.objects.filter(id=FeedItems.objects.last().id).update(source=xmltodict.parse(contents)['rss']['channel']['item'][item])
			if type(xmltodict.parse(contents)['rss']['channel']['item']) is list:
				for items in xmltodict.parse(contents)['rss']['channel']['item']:
					FeedItems.objects.create(feed_id=Feeds.objects.last().id)
					IntelReports.objects.create(feeditem_id=FeedItems.objects.last().id, feed_id=Feeds.objects.last().id, intelgroup_id=groupid)
					for item in items:
						if(item == 'title'):
							FeedItems.objects.filter(id=FeedItems.objects.last().id).update(title=items[item])
						elif(item == 'link'):
							FeedItems.objects.filter(id=FeedItems.objects.last().id).update(link=items[item])
						elif(item == 'description'):
							FeedItems.objects.filter(id=FeedItems.objects.last().id).update(description=items[item])
							text = json.dumps(items[item])
							results = extract.extract_observables(text)
							for result in results:
								if result == 'ipv4addr' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
								elif result == 'ipv4cidr' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
								elif result == 'ipv4range' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
								elif result == 'ipv6addr' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
								elif result == 'ipv6cidr' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
								elif result == 'ipv6range' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
								elif result == 'md5' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
								elif result == 'sha1' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
								elif result == 'sha256' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
								elif result == 'ssdeep' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
								elif result == 'fqdn' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
								elif result == 'url' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
								elif result == 'useragent' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
								elif result == 'email' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
								elif result == 'filename' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
								elif result == 'filepath' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
								elif result == 'regkey' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
								elif result == 'asn' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
								elif result == 'asnown' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
								elif result == 'country' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
								elif result == 'isp' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
								elif result == 'cve' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
								elif result == 'malware' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
								elif result == 'attacktype' and len(results[result])>0:
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif(item == 'author'):
							FeedItems.objects.filter(id=FeedItems.objects.last().id).update(author=items[item])
						elif(item == 'category'):
							FeedItems.objects.filter(id=FeedItems.objects.last().id).update(category=items[item])
						elif(item == 'comments'):
							FeedItems.objects.filter(id=FeedItems.objects.last().id).update(comments=items[item])
						elif(item == 'enclosure'):
							FeedItems.objects.filter(id=FeedItems.objects.last().id).update(enclosure=items[item])
						elif(item == 'guid'):
							FeedItems.objects.filter(id=FeedItems.objects.last().id).update(guid=items[item])
						elif(item == 'pubdate'):
							FeedItems.objects.filter(id=FeedItems.objects.last().id).update(pubdate=items[item])
						elif(item == 'source'):
							FeedItems.objects.filter(id=FeedItems.objects.last().id).update(source=items[item])
		groupids = []
		for role in UserIntelGroupRoles.objects.filter(intelgroup_id=request.data['intelgroup_id']).order_by('id').all():
			groupids.append(role.intelgroup_id)
		queryset = Feeds.objects.filter(intelgroup_id__in=groupids).order_by('id').all()
		serializer = FeedCategorySerializer(queryset, many=True)
		return Response(serializer.data)
	if request.method == 'PUT':
		data = request.data
		Feeds.objects.filter(id=data['id']).update(url=data['url'], name=data['name'], description=data['description'], category_id=data['category'], tags=data['tags'], manage_enabled=data['manage_enabled'], confidence=data['confidence'], updated_at=datetime.now())
		serializer = FeedCategorySerializer(Feeds.objects.filter(intelgroup_id=Feeds.objects.filter(id=request.data['id']).values()[0]['intelgroup_id']).order_by('id').all(), many=True)
		return Response(serializer.data)

@swagger_auto_schema(methods=['post'], request_body=IDSerializer, responses={201: FeedCategorySerializer})
@api_view(['POST'])
def feedlist(request):
	if not request.user.is_staff:
		created_at = IntelGroups.objects.filter(id=request.data['id']).last().created_at
		subid = IntelGroups.objects.filter(id=request.data['id']).last().plan_id
		customfeeds = True
		message = ''
		if subid != None:
			planid = Subscription.objects.filter(djstripe_id=subid).last().plan_id
			productid = Plan.objects.filter(djstripe_id=planid).last().product_id
			if Product.objects.filter(djstripe_id=productid).last().metadata['custom_feeds'] == 'false':
				customfeeds = False
		if UserIntelGroupRoles.objects.filter(user_id=request.user.id, intelgroup_id=request.data['id']).last().role == 2:
			feeds = Feeds.objects.filter(intelgroup_id=request.data['id']).order_by('id').all()
		if UserIntelGroupRoles.objects.filter(user_id=request.user.id, intelgroup_id=request.data['id']).last().role == 1:
			feeds = Feeds.objects.filter(intelgroup_id=request.data['id']).filter(manage_enabled='true').order_by('id').all()
		if UserIntelGroupRoles.objects.filter(user_id=request.user.id, intelgroup_id=request.data['id']).last().role == 0:
			feeds = Feeds.objects.filter(intelgroup_id=request.data['id']).filter(manage_enabled='true').order_by('id').all()
		feed_serializer = FeedCategorySerializer(feeds, many=True)
		categories = Categories.objects.order_by('id').all()
		category_serializer = CategorySerializer(categories, many=True)
		tags = Tags.objects.order_by('id').all()
		tag_serializer = TagSerializer(tags, many=True)
		currentrole = UserIntelGroupRoles.objects.filter(user_id=request.user.id, intelgroup_id=request.data['id']).all()
		role_serializer = UserGroupRoleSerializer(currentrole[0])
		return Response({'feedlist':feed_serializer.data, 'categories':category_serializer.data, 'tags':tag_serializer.data, 'currentrole': role_serializer.data,'customfeeds':customfeeds})

	if request.user.is_staff:
		if request.data['id'] == '':
			feeds = Feeds.objects.order_by('id').all()
		else:
			feeds = Feeds.objects.filter(intelgroup_id=request.data['id']).order_by('id').all()
		feed_serializer = FeedCategorySerializer(feeds, many=True)
		categories = Categories.objects.order_by('id').all()
		category_serializer = CategorySerializer(categories, many=True)
		tags = Tags.objects.order_by('id').all()
		tag_serializer = TagSerializer(tags, many=True)
		return Response({'feedlist':feed_serializer.data, 'categories':category_serializer.data, 'tags':tag_serializer.data})

@api_view(['POST'])
def feedlists(request):
	feeds = FeedCategorySerializer(Feeds.objects.filter(intelgroup_id=request.data['id']).order_by('id').all(), many=True)
	categories = CategorySerializer(Categories.objects.order_by('id').all(), many=True)
	tags = TagSerializer(Tags.objects.order_by('id').all(), many=True)
	return Response({'feedlist':feeds.data, 'categories':categories.data, 'tags':tags.data})

@swagger_auto_schema(methods=['post'], request_body=SearchFeedSerializer, responses={201: FeedCategorySerializer})
@api_view(['POST'])
def searchfeeds(request):
	data = []
	if not request.user.is_staff:
		currentgroup = int(request.data['currentgroup'])
		if(UserIntelGroupRoles.objects.filter(user_id=request.user.id, intelgroup_id=currentgroup).last().role == 2):
			if(request.data['category'] == '' and request.data['tags'] == '' and request.data['confidence'] == ''):
				data = Feeds.objects.filter(intelgroup_id=currentgroup).order_by('id').all()
			if(request.data['category'] != '' and request.data['tags'] == '' and request.data['confidence'] == ''):
				data = Feeds.objects.filter(intelgroup_id=currentgroup, category_id = request.data['category']).order_by('id').all()
			if(request.data['category'] == '' and request.data['tags'] != '' and request.data['confidence'] == ''):
				feedlist = Feeds.objects.filter(intelgroup_id=currentgroup).all()
				for feed in feedlist:
					if(request.data['tags'] in feed.tags):
						data.append(feed)
			if(request.data['confidence'] != '' and request.data['tags'] == '' and request.data['category'] == ''):
				data = Feeds.objects.filter(intelgroup_id=currentgroup, confidence__gte=request.data['confidence']).order_by('id').all()
			if(request.data['confidence'] != '' and request.data['category'] != '' and request.data['tags'] == ''):
				data = Feeds.objects.filter(intelgroup_id=currentgroup, confidence__gte=request.data['confidence'], category_id=request.data['category']).order_by('id').all()
			if(request.data['confidence'] != '' and request.data['tags'] != '' and request.data['category'] == ''):
				temp = Feeds.objects.filter(intelgroup_id=currentgroup, confidence__gte=request.data['confidence']).order_by('id').all()
				for t in temp:
					if(request.data['tags'] in t.tags):
						data.append(t)
			if(request.data['category'] != '' and request.data['tags'] != '' and request.data['confidence'] == ''):
				temp = Feeds.objects.filter(intelgroup_id=currentgroup, category_id = request.data['category']).order_by('id').all()
				for t in temp:
					if(request.data['tags'] in t.tags):
						data.append(t)
			if(request.data['category'] != '' and request.data['tags'] != '' and request.data['confidence'] != ''):
				temp = Feeds.objects.filter(intelgroup_id=currentgroup,  category_id = request.data['category'], confidence__gte=request.data['confidence']).order_by('id').all()
				for t in temp:
					if(request.data['tags'] in t.tags):
						data.append(t)
			serializer = FeedCategorySerializer(data, many=True)
			return Response(serializer.data)
		if(UserIntelGroupRoles.objects.filter(user_id=request.user.id, intelgroup_id=currentgroup).last().role == 1):
			if(request.data['category'] == '' and request.data['tags'] == '' and request.data['confidence'] == ''):
				data = Feeds.objects.filter(intelgroup_id=currentgroup, manage_enabled='true').order_by('id').all()
			if(request.data['category'] != '' and request.data['tags'] == '' and request.data['confidence'] == ''):
				data = Feeds.objects.filter(intelgroup_id=currentgroup, category_id = request.data['category'], manage_enabled='true').order_by('id').all()
			if(request.data['category'] == '' and request.data['tags'] != '' and request.data['confidence'] == ''):
				feedlist = Feeds.objects.filter(intelgroup_id=currentgroup, manage_enabled='true').all()
				for feed in feedlist:
					if(request.data['tags'] in feed.tags):
						data.append(feed)
			if(request.data['confidence'] != '' and request.data['tags'] == '' and request.data['category'] == ''):
				data = Feeds.objects.filter(intelgroup_id=currentgroup, confidence__gte=request.data['confidence'], manage_enabled='true').order_by('id').all()
			if(request.data['confidence'] != '' and request.data['category'] != '' and request.data['tags'] == ''):
				data = Feeds.objects.filter(intelgroup_id=currentgroup, confidence__gte=request.data['confidence'], manage_enabled='true', category_id=request.data['category']).order_by('id').all()
			if(request.data['confidence'] != '' and request.data['tags'] != '' and request.data['category'] == ''):
				temp = Feeds.objects.filter(intelgroup_id=currentgroup, confidence__gte=request.data['confidence'], manage_enabled='true').order_by('id').all()
				for t in temp:
					if(request.data['tags'] in t.tags):
						data.append(t)
			if(request.data['category'] != '' and request.data['tags'] != '' and request.data['confidence'] == ''):
				temp = Feeds.objects.filter(intelgroup_id=currentgroup, category_id = request.data['category'], manage_enabled='true').order_by('id').all()
				for t in temp:
					if(request.data['tags'] in t.tags):
						data.append(t)
			if(request.data['category'] != '' and request.data['tags'] != '' and request.data['confidence'] != ''):
				temp = Feeds.objects.filter(intelgroup_id=currentgroup, confidence__gte=request.data['confidence'], manage_enabled='true', category_id = request.data['category'])
				for t in temp:
					if(request.data['tags'] in t.tags):
						data.append(t)
			serializer = FeedCategorySerializer(data, many=True)
			return Response(serializer.data)
	if request.user.is_staff:
		if request.data['currentgroup'] != '':
			if(request.data['category'] == '' and request.data['tags'] == '' and request.data['confidence'] == ''):
				data = Feeds.objects.filter(intelgroup_id=request.data['currentgroup']).order_by('id').all()
			if(request.data['category'] != '' and request.data['tags'] == '' and request.data['confidence'] == ''):
				data = Feeds.objects.filter(intelgroup_id=request.data['currentgroup'], category_id = request.data['category']).order_by('id').all()
			if(request.data['category'] == '' and request.data['tags'] != '' and request.data['confidence'] == ''):
				feedlist = Feeds.objects.filter(intelgroup_id=request.data['currentgroup']).all()
				for feed in feedlist:
					if(request.data['tags'] in feed.tags):
						data.append(feed)
			if(request.data['confidence'] != '' and request.data['tags'] == '' and request.data['category'] == ''):
				data = Feeds.objects.filter(intelgroup_id=request.data['currentgroup'], confidence__gte=request.data['confidence']).order_by('id').all()
			if(request.data['confidence'] != '' and request.data['category'] != '' and request.data['tags'] == ''):
				data = Feeds.objects.filter(intelgroup_id=request.data['currentgroup'], confidence__gte=request.data['confidence'], category_id=request.data['category']).order_by('id').all()
			if(request.data['confidence'] != '' and request.data['tags'] != '' and request.data['category'] == ''):
				temp = Feeds.objects.filter(intelgroup_id=request.data['currentgroup'], confidence__gte=request.data['confidence']).order_by('id').all()
				for t in temp:
					if(request.data['tags'] in t.tags):
						data.append(t)
			if(request.data['category'] != '' and request.data['tags'] != '' and request.data['confidence'] == ''):
				temp = Feeds.objects.filter(intelgroup_id=request.data['currentgroup'], category_id = request.data['category']).order_by('id').all()
				for t in temp:
					if(request.data['tags'] in t.tags):
						data.append(t)
			if(request.data['category'] != '' and request.data['tags'] != '' and request.data['confidence'] != ''):
				temp = Feeds.objects.filter(intelgroup_id=request.data['currentgroup'], confidence__gte=request.data['confidence'], category_id = request.data['category'])
				for t in temp:
					if(request.data['tags'] in t.tags):
						data.append(t)
			serializer = FeedCategorySerializer(data, many=True)
			return Response(serializer.data)
		else:
			if(request.data['category'] == '' and request.data['tags'] == '' and request.data['confidence'] == ''):
				data = Feeds.objects.order_by('id').all()
			if(request.data['category'] != '' and request.data['tags'] == '' and request.data['confidence'] == ''):
				data = Feeds.objects.order_by('id').filter(category_id = request.data['category']).all()
			if(request.data['category'] == '' and request.data['tags'] != '' and request.data['confidence'] == ''):
				feedlist = Feeds.objects.all()
				for feed in feedlist:
					if(request.data['tags'] in feed.tags):
						data.append(feed)
			if(request.data['confidence'] != '' and request.data['tags'] == '' and request.data['category'] == ''):
				data = Feeds.objects.filter(confidence__gte=request.data['confidence']).order_by('id').all()
			if(request.data['confidence'] != '' and request.data['category'] != '' and request.data['tags'] == ''):
				data = Feeds.objects.filter(confidence__gte=request.data['confidence'], category_id=request.data['category']).order_by('id').all()
			if(request.data['confidence'] != '' and request.data['tags'] != '' and request.data['category'] == ''):
				temp = Feeds.objects.filter(confidence__gte=request.data['confidence']).order_by('id').all()
				for t in temp:
					if(request.data['tags'] in t.tags):
						data.append(t)
			if(request.data['category'] != '' and request.data['tags'] != '' and request.data['confidence'] == ''):
				temp = Feeds.objects.order_by('id').filter(category_id = request.data['category']).all()
				for t in temp:
					if(request.data['tags'] in t.tags):
						data.append(t)
			if(request.data['category'] != '' and request.data['tags'] != '' and request.data['confidence'] != ''):
				temp = Feeds.objects.filter(confidence__gte=request.data['confidence'], category_id = request.data['category'])
				for t in temp:
					if(request.data['tags'] in t.tags):
						data.append(t)
			serializer = FeedCategorySerializer(data, many=True)
			return Response(serializer.data)

@swagger_auto_schema(methods=['post'], request_body=AttributeCreateSerializer, responses={201: UserGroupAttributeSerializer})
@swagger_auto_schema(methods=['put'], request_body=AttributeUpdateSerializer, responses={200: UserGroupAttributeSerializer})
@api_view(['POST', 'PUT'])
def attributes(request):
	if request.method == 'POST':
		if 'attribute' in request.data:
			for attribute in Attributes.objects.filter(user_id=request.user.id, intelgroup_id=request.data['currentgroup']):
				if attribute.attribute == request.data['attribute'] and attribute.value == request.data['value']:
					return Response({'message':True})
			Attributes.objects.create(attribute=request.data['attribute'],api_attribute='_'.join(request.data['attribute'].split(' ')).lower(), value=request.data['value'], api_value='_'.join(request.data['value'].split(' ')).lower(), words_matched=request.data['words_matched'], isenable=request.data['isenable'], user_id=request.user.id, intelgroup_id=request.data['currentgroup'])
			create_data = Attributes.objects.filter(user_id=request.user.id).last()
			serializer = UserGroupAttributeSerializer(create_data)
			return Response(serializer.data)
		else:
			created_at = IntelGroups.objects.filter(id=request.data['currentgroup']).last().created_at
			subid = IntelGroups.objects.filter(id=request.data['currentgroup']).last().plan_id
			customobservable = True
			if subid != None:
				planid = Subscription.objects.filter(djstripe_id=subid).last().plan_id
				productid = Plan.objects.filter(djstripe_id=planid).last().product_id
				if Product.objects.filter(djstripe_id=productid).last().metadata['custom_observables'] == 'false':
					customobservable = False
			attributes = Attributes.objects.filter(intelgroup_id=request.data['currentgroup']).order_by('id').all()
			attribute_serializer = UserGroupAttributeSerializer(attributes, many=True)
			enableglobalattributes = GroupGlobalAttributeSerializer(GroupGlobalAttributes.objects.filter(intelgroup_id=request.data['currentgroup']).all(), many=True)
			currentrole = UserIntelGroupRoles.objects.filter(user_id=request.user.id, intelgroup_id=request.data['currentgroup']).all()
			role_serializer = UserGroupRoleSerializer(currentrole[0])
			return Response({'attributes':attribute_serializer.data, 'currentrole':role_serializer.data, 'globalattributes':enableglobalattributes.data, 'customobservable':customobservable})
	elif request.method == 'PUT':
		Attributes.objects.filter(id=request.data['id']).update(attribute=request.data['attribute'],api_attribute='_'.join(request.data['attribute'].split(' ')).lower(), value=request.data['value'], api_value='_'.join(request.data['value'].split(' ')).lower(), words_matched=request.data['words_matched'], isenable=request.data['isenable'], user_id=request.user.id, intelgroup_id=request.data['currentgroup'])
		serializer = UserGroupAttributeSerializer(Attributes.objects.filter(id=request.data['id']).all()[0])
		return Response(serializer.data)

@api_view(['POST'])
def enableglobal(request):
	GroupGlobalAttributes.objects.filter(id=request.data['id']).update(isenable=request.data['isenable'])
	serializer = GroupGlobalAttributeSerializer(GroupGlobalAttributes.objects.filter(id=request.data['id']).last())
	return Response(serializer.data)

@swagger_auto_schema(methods=['post'], request_body=AttributeCreateSerializer, responses={201: UserGroupAttributeSerializer})
@swagger_auto_schema(methods=['put'], request_body=AttributeUpdateSerializer, responses={200: UserGroupAttributeSerializer})
@api_view(['POST', 'PUT'])
def whitelist(request):
	if request.method == 'POST':
		if not 'indicator' in request.data:
			feedids = [];
			feeditemids = [];
			for feed in Feeds.objects.filter(intelgroup_id=request.data['currentgroup']).all():
				feedids.append(feed.id)
			for feeditem in FeedItems.objects.filter(feed_id__in=feedids).all():
				feeditemids.append(feeditem.id)
			indicators = Indicators.objects.filter(feeditem_id__in=feeditemids).order_by('id').all()
			whitelist = Whitelists.objects.order_by('id').all()
			globalindicators = GlobalIndicators.objects.order_by('id').all()	
			indicator_serializer = IndicatorGlobalSerializer(indicators, many=True)
			whitelist_serializer = UserIndicatorWhitelistSerializer(whitelist, many=True)
			global_serializer = GlobalIndicatorSerializer(globalindicators, many=True)
			currentrole = UserIntelGroupRoles.objects.filter(user_id=request.user.id, intelgroup_id=request.data['currentgroup']).all()
			serializer = UserGroupRoleSerializer(currentrole[0])
			return Response({'indicators': indicator_serializer.data, 'whitelist': whitelist_serializer.data, 'globalindicators': global_serializer.data, 'currentrole': serializer.data})
		else:
			Whitelists.objects.create(indicator_id=request.data['indicator'],value=request.data['value'], user_id=request.user.id, enabled=request.data['enabled'] )
			create_data = Whitelists.objects.last()
			serializer = UserIndicatorWhitelistSerializer(create_data)
			return Response(serializer.data)
	if request.method == 'PUT':
		Whitelists.objects.filter(id=request.data['id']).update(enabled=request.data['enabled'])
		serializer = UserIndicatorWhitelistSerializer(Whitelists.objects.filter(id=request.data['id']).last())
		return Response(serializer.data)

@swagger_auto_schema(methods=['put'], request_body=EnabledSerializer, responses={200: GlobalItemIndicatorSerializer})
@api_view(['PUT'])
def indicators(request):
	Indicators.objects.filter(id=request.data['id']).update(enabled=request.data['enabled'])
	serializer = GlobalItemIndicatorSerializer(Indicators.objects.filter(id=request.data['id']).all()[0])
	return Response(serializer.data)

@swagger_auto_schema(methods=['post'], request_body=InviteSerializer, responses={201: UserIntelGroupRolesSerializer})
@api_view(['POST'])
def invite(request):
	created_at = IntelGroups.objects.filter(id=request.data['group_id']).last().created_at
	subid = IntelGroups.objects.filter(id=request.data['group_id']).last().plan_id
	flag = False
	if subid == None:
		if datetime.now()<created_at.replace(tzinfo=None)+timedelta(days=30):
			flag =True			
	else:
		planid = Subscription.objects.filter(djstripe_id=subid).last().plan_id
		productid = Plan.objects.filter(djstripe_id=planid).last().product_id
		max_users = Product.objects.filter(djstripe_id=productid).last().metadata['max_users']
		users = UserIntelGroupRoles.objects.filter(intelgroup_id=request.data['group_id']).all()
		if len(users) < int(max_users):
			flag = True
	if flag:
		groupname = IntelGroups.objects.filter(id=request.data['group_id']).all()[0].name
		message = Mail(
			from_email='kardzavaryan@gmail.com',
			to_emails=request.data['emails'],
			subject=f'You’ve been invited to join the {groupname} Intel Group on Cyobstract',
			html_content=f'''<strong>From:</strong><span>sherlock@mg.cyobstract.com</span><br/>
			<strong>Name:</strong><span>Sherlock at Cyobstract</span><br/>
			<strong>Reply-to:</strong><span>sherlock@cyobstract.com</span><br/>
			<strong>Title:</strong><span>You've been invited to join the {groupname} Intel Group on Cyobstract</span><br/>
			<p>Hello!</p>
			<p>kardzavaryan@gmail.com has invited to join the {groupname} Intel Group on Cyobstract as a Member.</p>
			<p>By accepting this invitation, you’ll have access to all intelligence curated by the other members of the {groupname} Intel Group.</p>
			<p>To confirm or reject this invitation, click the link below.</p>
			<p><a href="http://sherlock-staging.obstractai.com">sherlock-staging.obstractai.com</a></p>
			<p>If you have any questions, simply reply to this email to get in contact with a real person on the team.</p>
			<p>Sherlock and the Cyobstract Team</p>''')
		try:
			sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
			response = sg.send(message)
			print(response.status_code)
		except Exception as e:
			print(str(e))
		data = [];
		for userid in request.data['userids']:
			existing_user = UserIntelGroupRoles.objects.filter(intelgroup_id=request.data['group_id'], user_id=userid).all()
			if len(existing_user) == 0:
				UserIntelGroupRoles.objects.create(intelgroup_id=request.data['group_id'], user_id=userid, role=0)
				user = UserIntelGroupRoles.objects.filter(intelgroup_id=request.data['group_id'], user_id=userid, role=0).all()
				serializer = UserIntelGroupRolesSerializer(user[0])
				data.append(serializer.data)
		if(len(data) == 0):
				data=[{'role': 'success'}]
		return Response(data)
	else:
		return Response({'message':True})

@swagger_auto_schema(methods=['post'], request_body=IDSerializer, responses={201: UserGroupRoleSerializer})
@api_view(['POST'])
def currentrole(request):
	currentrole = UserIntelGroupRoles.objects.filter(user_id=request.user.id, intelgroup_id=request.data['id']).all()
	serializer = UserGroupRoleSerializer(currentrole[0])
	return Response({'currentrole':serializer.data})

@swagger_auto_schema(methods=['post'], request_body=CategoryCreateSerializer, responses={201: CategorySerializer})
@swagger_auto_schema(methods=['put'], request_body=CategoryUpdateSerializer, responses={200: CategorySerializer})
@swagger_auto_schema(methods=['delete'], request_body=IDSerializer, responses={204: CategorySerializer})
@api_view(['POST', 'PUT', 'DELETE'])
def categories(request):
	if request.method == 'POST':
		if not 'name' in request.data:
			categorylist = Categories.objects.order_by('id').all()
			category_serializer = CategorySerializer(categorylist, many=True)
			currentrole = UserIntelGroupRoles.objects.filter(user_id=request.user.id, intelgroup_id=request.data['currentgroup']).all()
			serializer = UserGroupRoleSerializer(currentrole[0])
			return Response({'currentrole':serializer.data, 'categorylist':category_serializer.data})
		else:
			Categories.objects.create(name=request.data['name'])
			category_serializer = CategorySerializer(Categories.objects.order_by('id').last())
			return Response(category_serializer.data)
	if request.method == 'PUT':
		Categories.objects.filter(id=request.data['id']).update(name=request.data['name'])
		serializer = CategorySerializer(Categories.objects.filter(id=request.data['id']).all()[0])
		return Response(serializer.data)
	if request.method == 'DELETE':
		Categories.objects.filter(id=request.data['id']).delete()
		return Response({"Successfully deleted!"})

# @swagger_auto_schema(methods=['get'], responses={200: GlobalIndicatorSerializer})
# @swagger_auto_schema(methods=['post'], request_body=GlobalIndicatorCreateSerializer, responses={201: UserGlobalIndicatorSerializer})
# @swagger_auto_schema(methods=['put'], request_body=EnabledSerializer, responses={200: UserGlobalIndicatorSerializer})
# @api_view(['GET', 'POST', 'PUT'])
# def globalindicators(request):
# 	if request.method == 'GET':
# 		globalindicators = GlobalIndicators.objects.order_by('id').all()
# 		globalindicator_serializer = GlobalIndicatorSerializer(globalindicators, many=True)
# 		return Response({'globalindicators':globalindicator_serializer.data})
# 	if request.method == 'POST':
# 		GlobalIndicators.objects.create(type=request.data['type'], type_api=request.data['type_api'], value=request.data['value'], value_api=request.data['value_api'], user_id=request.user.id, enabled=request.data['enabled'])
# 		serializer = UserGlobalIndicatorSerializer(GlobalIndicators.objects.last())
# 		return Response(serializer.data)
# 	if request.method == 'PUT':
# 		GlobalIndicators.objects.filter(id=request.data['id']).update(enabled=request.data['enabled'])
# 		serializer = UserGlobalIndicatorSerializer(GlobalIndicators.objects.filter(id=request.data['id']).last())
# 		return Response(serializer.data)

# @swagger_auto_schema(methods=['post'], request_body=GlobalAttributeCreateSerializer, responses={201: UserGroupGlobalAttributeSerializer})
# @swagger_auto_schema(methods=['put'], request_body=GlobalAttributeUpdateSerializer, responses={200: UserGroupGlobalAttributeSerializer})
# @api_view(['POST', 'PUT'])
# def globalattributes(request):
# 	if request.method == 'POST':
# 		if not 'attribute' in request.data:
# 			if request.data['currentgroup'] == '':
# 				attributelist = GlobalAttributes.objects.filter(user_id=request.user.id).order_by('id').all()
# 				attribute_serializer = UserGroupGlobalAttributeSerializer(attributelist, many=True)
# 			else:
# 				attributelist = GlobalAttributes.objects.filter(user_id=request.user.id, intelgroup_id=request.data['currentgroup']).order_by('id').all()
# 				attribute_serializer = UserGroupGlobalAttributeSerializer(attributelist, many=True)
# 			return Response({'globalattributes':attribute_serializer.data})
# 		else:
# 			GlobalAttributes.objects.create(attribute=request.data['attribute'], api_attribute='_'.join(request.data['attribute'].split(' ')).lower(), value=request.data['value'], api_value='_'.join(request.data['value'].split(' ')).lower(), words_matched=request.data['words_matched'], enabled=request.data['enabled'], user_id=request.user.id, intelgroup_id=request.data['currentgroup'])
# 			attribute = GlobalAttributes.objects.filter(user_id=request.user.id).last()
# 			attribute_serializer = UserGroupGlobalAttributeSerializer(attribute)
# 			return Response(attribute_serializer.data)
# 	if request.method == 'PUT':
# 		GlobalAttributes.objects.filter(id=request.data['id']).update(attribute=request.data['attribute'], value=request.data['value'], words_matched=request.data['words_matched'], enabled=request.data['enabled'], user_id=request.user.id, intelgroup_id=request.data['currentgroup'])
# 		attribute = GlobalAttributes.objects.filter(id=request.data['id']).all()
# 		attribute_serializer = UserGroupGlobalAttributeSerializer(attribute[0])
# 		return Response(attribute_serializer.data)

@swagger_auto_schema(methods=['get'], responses={200: RoleGroupSerializer})
@api_view(['GET'])
def home(request):
	ftr = "http://ftr-premium.fivefilters.org/"
	# encode = urllib.parse.quote_plus("https://apnews.com/apf-topnews")
	encode = urllib.parse.quote_plus("http://feeds.bbci.co.uk/news/rss.xml")
	# encode = urllib.parse.quote_plus("https://www.microsoft.com/security/blog/security-blog-series/")
	key = urllib.parse.quote_plus("KSF8GH22GZRKA8")
	req = urllib.request.Request(ftr+"makefulltextfeed.php?url="+encode+"&key="+key+"&max=25")
	# req = urllib.request.Request("http://ftr-premium.fivefilters.org/makefulltextfeed.php?url=http://feeds.bbci.co.uk/news/rss.xml&key=KSF8GH22GZRKA8&summary=1&max=1&links=remove&content=1&xss=1&lang=2&parser=html5php&accept=application/json")
	contents = urllib.request.urlopen(req).read()
	text = json.dumps(xmltodict.parse(contents)['rss']['channel']['item'])
	# text = json.dumps(xmltodict.parse(contents))
	results = extract.extract_observables(text)
	print(','.join(results['topic']))
	for result in results:
		print(result)
	groups = RoleGroupSerializer(UserIntelGroupRoles.objects.order_by('id').filter(user_id=request.user.id).all(), many=True)
	users = CustomUserSerializer(CustomUser.objects.order_by('id').all(), many=True)
	intelgroups = IntelGroupSerializer(IntelGroups.objects.order_by('id').all(), many=True)
	return Response({'mygroups':groups.data, 'users':users.data, 'intelgroups':intelgroups.data, 're':results})

@swagger_auto_schema(methods=['delete'], request_body=IDSerializer, responses={200: RoleGroupSerializer})
@api_view(['DELETE'])
def leavegroup(request):
	result = []
	role = UserIntelGroupRoles.objects.filter(id=request.data['id']).last().role
	if role == 1:
		UserIntelGroupRoles.objects.filter(id=request.data['id']).delete()
		groups = UserIntelGroupRoles.objects.order_by('id').filter(user_id=request.user.id).all()
		for group in groups:
			serializer = RoleGroupSerializer(group)
			result.append(serializer.data)
	elif role == 2:
		intelgroup_id = UserIntelGroupRoles.objects.filter(id=request.data['id']).all()[0].intelgroup_id
		admins = UserIntelGroupRoles.objects.filter(intelgroup_id=intelgroup_id, role=2).all()
		users = UserIntelGroupRoles.objects.filter(intelgroup_id=intelgroup_id).all()
		if len(admins)==1:
			if len(users)==1:
				UserIntelGroupRoles.objects.filter(id=request.data['id']).delete()
				IntelGroups.objects.filter(id=intelgroup_id).delete()
				groups = UserIntelGroupRoles.objects.order_by('id').filter(user_id=request.user.id).all()
				for group in groups:
					serializer = RoleGroupSerializer(group)
					result.append(serializer.data)
			else:
				return Response({'message':True})
		else:
			UserIntelGroupRoles.objects.filter(id=request.data['id']).delete()
			groups = UserIntelGroupRoles.objects.order_by('id').filter(user_id=request.user.id).all()
			for group in groups:
				serializer = RoleGroupSerializer(group)
				result.append(serializer.data)

	return Response(result)

@swagger_auto_schema(methods=['get'], responses={200: RoleGroupSerializer})
@api_view(['GET'])
def deleteaccount(request):
	groups = UserIntelGroupRoles.objects.filter(user_id=request.user.id).all()
	if len(groups)>0:
		return Response({'message':True})
	else:
		CustomUser.objects.filter(id=request.user.id).delete()
		return Response({'delete':True})

@swagger_auto_schema(methods=['get'], responses={200: RoleGroupSerializer})
@swagger_auto_schema(methods=['post'], request_body=IntelgroupCreateSerializer, responses={201: RoleGroupSerializer})
@swagger_auto_schema(methods=['put'], request_body=IntelgroupUpdateSerializer, responses={200: RoleGroupSerializer})
@api_view(['GET', 'POST', 'PUT'])
def intelgroups(request):
	if request.method == 'GET':
		groups = RoleGroupSerializer(UserIntelGroupRoles.objects.filter(user_id=request.user.id).order_by('id').all(), many=True)
		users = CustomUserSerializer(CustomUser.objects.exclude(is_staff=True).order_by('id').all(), many=True)
		return Response({'intelgroups':groups.data, 'users':users.data})
	if request.method == 'POST':
		if 'name' in request.data:
			name = ''
			if(request.data['name'] == ''):
				letters = string.digits
				name = 'Intel Group' + ''. join(random.choice(letters) for i in range(10))
			else:
				name = request.data['name']
			message = Mail(
				from_email='kardzavaryan@gmail.com',
				to_emails=request.data['emails'],
				subject=f'You’ve been invited to join the {name} Intel Group on Cyobstract',
				html_content=f'''<strong>From:</strong><span>sherlock@mg.cyobstract.com</span><br/>
				<strong>Name:</strong><span>Sherlock at Cyobstract</span><br/>
				<strong>Reply-to:</strong><span>sherlock@cyobstract.com</span><br/>
				<strong>Title:</strong><span>You've been invited to join the {name} Intel Group on Cyobstract</span><br/>
				<p>Hello!</p>
				<p>kardzavaryan@gmail.com has invited to join the {name} Intel Group on Cyobstract as a Member.</p>
				<p>By accepting this invitation, you’ll have access to all intelligence curated by the other members of the {name} Intel Group.</p>
				<p>To confirm or reject this invitation, click the link below.</p>
				<p><a href="http://sherlock-staging.obstractai.com">sherlock-staging.obstractai.com</a></p>
				<p>If you have any questions, simply reply to this email to get in contact with a real person on the team.</p>
				<p>Sherlock and the Cyobstract Team</p>''')
			try:
				sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
				response = sg.send(message)
				print(response.status_code)
			except Exception as e:
				print(str(e))
			IntelGroups.objects.create(name=name, description=request.data['description'])
			new_group = IntelGroups.objects.last()
			UserIntelGroupRoles.objects.create(intelgroup_id=new_group.id, user_id=request.user.id, role=2)
			for invite_id in request.data['userids']:
				if invite_id != request.user.id:
					UserIntelGroupRoles.objects.create(intelgroup_id=new_group.id, user_id=invite_id, role=0)
			new_role = UserIntelGroupRoles.objects.filter(intelgroup_id=new_group.id, user_id=request.user.id).all()
			serializer = RoleGroupSerializer(new_role[0])
			return Response(serializer.data)
		else:
			name = IntelGroups.objects.filter(id=request.data['id']).last().name
			description = IntelGroups.objects.filter(id=request.data['id']).last().description
			role = UserGroupRoleSerializer(UserIntelGroupRoles.objects.filter(user_id=request.user.id, intelgroup_id=request.data['id']).all()[0])
			return Response({'name':name, 'description':description, 'currentrole':role.data})
	if request.method == 'PUT':
		IntelGroups.objects.filter(id=request.data['id']).update(name=request.data['name'],description=request.data['description'])
		new_role = UserIntelGroupRoles.objects.filter(intelgroup_id=request.data['id'], user_id=request.user.id).all()
		serializer = RoleGroupSerializer(new_role[0])
		return Response(serializer.data)

@swagger_auto_schema(methods=['put'], request_body=ManageEnabledSerializer, responses={200: FeedCategorySerializer})
@api_view(['PUT'])
def feedenable(request):
	Feeds.objects.filter(id=request.data['id']).update(manage_enabled=request.data['manage_enabled'])
	feeds = Feeds.objects.filter(intelgroup_id=Feeds.objects.filter(id=request.data['id']).last().intelgroup_id).order_by('id').all()
	serializer = FeedCategorySerializer(feeds, many=True)
	return Response(serializer.data)

@swagger_auto_schema(methods=['post'], request_body=AccepInviteSerializer, responses={201: RoleGroupSerializer})
@api_view(['POST'])
def acceptinvite(request):
	UserIntelGroupRoles.objects.filter(id=request.data['id']).update(role = '1')
	userid = UserIntelGroupRoles.objects.filter(id=request.data['id']).last().user_id
	useremail = CustomUser.objects.filter(id=userid).last().email
	groupid = UserIntelGroupRoles.objects.filter(id=request.data['id']).last().intelgroup_id
	groupname = IntelGroups.objects.filter(id=groupid).last().name
	message = Mail(
		from_email='kardzavaryan@gmail.com',
		to_emails=request.user.email,
		subject=f'You’ve been invited to join the {groupname} Intel Group on Cyobstract',
		html_content=f'''<strong>From:</strong><span>sherlock@mg.cyobstract.com</span><br/>
		<strong>Name:</strong><span>Sherlock at Cyobstract</span><br/>
		<strong>Reply-to:</strong><span>sherlock@cyobstract.com</span><br/>
		<strong>Title:</strong><span>{useremail} has accepted your invitation to join {groupname}</span><br/>
		<p>Hello!</p>
		<p>This email is just to confirm {useremail} has accepted your invitation to join {groupname}</p>
		<p>To manage members in your intel group, click the link below.</p>
		<p><a href="http://sherlock-staging.obstractai.com">sherlock-staging.obstractai.com</a></p>
		<p>Sherlock and the Cyobstract Team</p>''')
	try:
		sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
		response = sg.send(message)
		print(response.status_code)
	except Exception as e:
		print(str(e))
	groups = UserIntelGroupRoles.objects.order_by('id').filter(user_id=request.user.id).all()
	result = RoleGroupSerializer(groups, many=True)
	return Response(result.data)

@swagger_auto_schema(methods=['delete'], request_body=IDSerializer, responses={204: RoleGroupSerializer})
@api_view(['DELETE'])
def rejectinvite(request):
	userid = UserIntelGroupRoles.objects.filter(id=request.data['id']).last().user_id
	useremail = CustomUser.objects.filter(id=userid).last().email
	groupid = UserIntelGroupRoles.objects.filter(id=request.data['id']).last().intelgroup_id
	groupname = IntelGroups.objects.filter(id=groupid).last().name
	UserIntelGroupRoles.objects.filter(id=request.data['id']).delete()
	message = Mail(
		from_email='kardzavaryan@gmail.com',
		to_emails=request.user.email,
		subject=f'You’ve been invited to join the {groupname} Intel Group on Cyobstract',
		html_content=f'''<strong>From:</strong><span>sherlock@mg.cyobstract.com</span><br/>
		<strong>Name:</strong><span>Sherlock at Cyobstract</span><br/>
		<strong>Reply-to:</strong><span>sherlock@cyobstract.com</span><br/>
		<strong>Title:</strong><span>{useremail} has rejected your invitation to join {groupname}</span><br/>
		<p>Hello!</p>
		<p>{useremail} has rejected your invitation to join {groupname}</p>
		<p>If you think this is a mistake, you can resend the invitation to {useremail} to join {groupname}.</p>
		<p>To manage members in your intel group, click the link below:</p>
		<p><a href="http://sherlock-staging.obstractai.com">sherlock-staging.obstractai.com</a></p>
		<p>Sherlock and the Cyobstract Team</p>''')
	try:
		sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
		response = sg.send(message)
		print(response.status_code)
	except Exception as e:
		print(str(e))
	groups = UserIntelGroupRoles.objects.order_by('id').filter(user_id=request.user.id).all()
	result = RoleGroupSerializer(groups, many=True)
	return Response(result.data)

@swagger_auto_schema(methods=['put'], request_body=RoleUpdateSerializer, responses={200: UserIntelGroupRolesSerializer})
@swagger_auto_schema(methods=['delete'], request_body=IDSerializer, responses={204: UserIntelGroupRolesSerializer})
@api_view(['PUT', 'DELETE'])
def role(request):
	if request.method == 'PUT':
		UserIntelGroupRoles.objects.filter(id=request.data['id']).update(role=request.data['role'])
		user_role = UserIntelGroupRoles.objects.filter(intelgroup_id=request.data['groupid'], user_id=request.user.id).last().role
		serializer = UserIntelGroupRolesSerializer(UserIntelGroupRoles.objects.filter(intelgroup_id=request.data['groupid']).all(), many=True)
		return Response({'myId':request.user.id, 'users':serializer.data, 'grouprole':user_role})
	if request.method == 'DELETE':
		UserIntelGroupRoles.objects.filter(id=request.data['id']).delete()
		return Response('Success')

@swagger_auto_schema(methods=['get'], responses={200: CustomUserSerializer})
@swagger_auto_schema(methods=['post'], request_body=IDSerializer, responses={201: UserGroupRoleSerializer})
@api_view(['GET', 'POST'])
def users(request):
	if request.method == 'GET':
		serializer = CustomUserSerializer(CustomUser.objects.exclude(is_staff=True).order_by('id').all(), many=True)
		return Response(serializer.data)
	if request.method == 'POST':
		user_role = UserGroupRoleSerializer(UserIntelGroupRoles.objects.all().filter(intelgroup_id=request.data['id'], user_id=request.user.id).last())
		serializer = UserGroupRoleSerializer(UserIntelGroupRoles.objects.filter(intelgroup_id=request.data['id']).all(), many=True)
		return Response({'myId':request.user.id, 'users':serializer.data, 'grouprole':user_role.data})

@swagger_auto_schema(methods=['post'], request_body=IDSerializer, responses={201: UserIntelGroupRolesSerializer})
@api_view(['POST'])
def changegroup(request, subscription_holder=None):
    
	isPlan = True
	isInit = False
	isAutoDown = False
	message = ''
	subid = IntelGroups.objects.filter(id=request.data['id']).last().plan_id
	created_at = IntelGroups.objects.filter(id=request.data['id']).last().created_at
	currentrole = UserGroupRoleSerializer(UserIntelGroupRoles.objects.filter(user_id=request.user.id, intelgroup_id=request.data['id']).last())
	if not CustomUser.objects.filter(id=request.user.id).last().is_staff:
		if subid == None:
			if datetime.now() < created_at.replace(tzinfo=None)+timedelta(days=30):
				isInit = True
				date = str(created_at.replace(tzinfo=None)+timedelta(days=30)).split(' ')[0]
				message = f'Your plan will be downgraded and limited on {date}, to keep all existing features, you must select a plan before this date.'
			else:
				isPlan = False
		else:
			current_period_end = Subscription.objects.filter(djstripe_id=subid).last().current_period_end
			if datetime.now() > current_period_end.replace(tzinfo=None):
				starterid = Plan.objects.filter(interval='month', amount=0).last().djstripe_id
				Subscription.objects.filter(djstripe_id=subid).update(plan_id=starterid)
				isAutoDown = True
		
	return Response({'isPlan':isPlan, 'isInit':isInit, 'isAutoDown':isAutoDown, 'message':message, 'currentrole':currentrole.data})