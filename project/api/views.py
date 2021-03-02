import json
import os
import random
import secrets
import string
import sys
import urllib
from datetime import datetime, timedelta
from itertools import chain
from urllib.parse import urlencode

import requests
import stripe
import xmltodict
from cyobstract import extract
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from dotenv import load_dotenv
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()
from apps.users.models import CustomUser
from dateutil import parser as dateutil_parser
from djstripe.models import Plan, Product, Subscription
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from pegasus.apps.examples.tasks import progress_bar_task
from rest_framework import generics
from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string

from ..models import (APIKeys, Attributes, Categories, FeedChannels, FeedItems,
                      Feeds, GlobalAttributes, GlobalIndicators, GroupFeeds,
                      GroupGlobalAttributes, Indicators, IntelGroups,
                      IntelReports, PlanHistory, Tags, UserIntelGroupRoles,
                      WebHooks, Whitelists)
from ..serializers import (AccepInviteSerializer, APIKeyCreateSerializer,
                           APIkeySerializer, AttributeCreateSerializer,
                           AttributeUpdateSerializer, CategoryCreateSerializer,
                           CategorySerializer, CategoryUpdateSerializer,
                           ChangeEmailSerializer,
                           CustomUserSerializer, EnabledSerializer,
                           FeedCategorySerializer, FeedChannelSerializer,
                           FeedCreateSerializer, FeedItemSerializer,
                           FeedUpdateSerializer, GlobalAttributeSerializer,
                           GlobalIndicatorSerializer,
                           GlobalItemIndicatorSerializer,
                           GroupCategoryFeedSerializer,
                           GroupGlobalAttributeSerializer, GroupIDSerializer,
                           GroupRoleSerializer, GroupWebHookSerializer,
                           IDSerializer, IndicatorGlobalSerializer,
                           IntelgroupCreateSerializer, IntelGroupSerializer,
                           IntelgroupUpdateSerializer, InviteSerializer,
                           ItemFeedGroupReportSerializer,
                           ItemIndicatorSerializer, RoleGroupSerializer,
                           RoleUpdateSerializer, SearchFeedSerializer,
                           SearchReportSerializer, TagSerializer,
                           UserGlobalIndicatorSerializer,
                           UserGroupAttributeSerializer,
                           UserGroupRoleSerializer,APIFeedSerializer,
                           UserIndicatorWhitelistSerializer,APIReportSerializer,
                           UserIntelGroupRolesSerializer, UserSerializer,
                           WebhookCreateSerializer, WebhookUpdateSerializer,
                           WhitelistCreateSerializer, APIGroupSerializer)

uuid = openapi.Parameter('UUID', openapi.IN_QUERY, description="feed UUID", type=openapi.TYPE_STRING)
groupids = openapi.Parameter('groupids', openapi.IN_QUERY, description="Intel Group UUIDs", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING))
confidence = openapi.Parameter('confidence', openapi.IN_QUERY, description="Feed confidence", type=openapi.TYPE_NUMBER)
category = openapi.Parameter('category', openapi.IN_QUERY, description="Feed category", type=openapi.TYPE_NUMBER)
tags = openapi.Parameter('tags', openapi.IN_QUERY, description="Feed tags", type=openapi.TYPE_STRING)
created_at = openapi.Parameter('created_at', openapi.IN_QUERY, description="Feed created_at(eg:2020-02-03)", type=openapi.TYPE_STRING)
updated_at = openapi.Parameter('updated_at', openapi.IN_QUERY, description="Feed updated_at(eg:2020-02-03)", type=openapi.TYPE_STRING)
@csrf_exempt
@swagger_auto_schema(methods=['get'], manual_parameters=[uuid, groupids, confidence, category, tags, created_at, updated_at], responses={200: APIFeedSerializer(many=True)})
@api_view(['GET'])
def apifeeds(request):
	if request.method == 'POST':
		body_unicode = request.body.decode('utf-8')
		body = json.loads(body_unicode)
	elif request.method == 'GET':
		body = request.GET
	
	userid = 0
	groupids = []
	tempids = []
	for apikey in APIKeys.objects.all():
		if apikey.value == request.headers['x-api-key']:
			tempids = apikey.groupids.split(',')
			userid = apikey.user_id
	if userid == 0:
		return render(request, 'project/feeds.html', {'feeds':'This is invalid apikey.'})
	
	if 'UUID' in body:
		if len(GroupFeeds.objects.filter(uniqueid=body['UUID']).all()) == 0:
			return render(request, 'project/feeds.html', {'feeds':"The feed doesn't exist."})
		else:
			subid = IntelGroups.objects.filter(id=GroupFeeds.objects.filter(uniqueid=body['UUID']).last().intelgroup_id).last().plan_id
			if subid == None:
				return render(request, 'project/feeds.html', {'feeds':'Your Intel Group must upgrade to perfrom this action.'})
			else:
				planid = Subscription.objects.filter(djstripe_id=subid).last().plan_id
				productid = Plan.objects.filter(djstripe_id=planid).last().product_id
				api_access = Product.objects.filter(djstripe_id=productid).last().metadata['api_access']
				current_period_end = Subscription.objects.filter(djstripe_id=subid).last().current_period_end
				if api_access and current_period_end.replace(tzinfo=None) > datetime.now():
					feed = GroupCategoryFeedSerializer(GroupFeeds.objects.filter(uniqueid=body['UUID']).last()).data
					data = {
						'UUID': body['UUID'],
						'Type': feed['feed']['type'],
						'Feed name': feed['name'],
						'Feed description': feed['description'],
						'Feed_URL': feed['feed']['url'],
						'Intel_Group_UUID': feed['intelgroup']['uniqueid'],
						'Confidence': feed['confidence'],
						'Category': feed['category']['name'],
						'Tags': feed['tags'],
						'Datetime_created': feed['created_at'],
						'Datetime_last_polled': feed['updated_at'],
						'Dateteim_last_data': feed['updated_at'],
						'RSS': FeedChannelSerializer(FeedChannels.objects.filter(feed_id=feed['feed']['id']).last()).data
					}
					return render(request, 'project/feeds.html', {'feeds':json.dumps(data)})
				else:
					return render(request, 'project/feeds.html', {'feeds':'Your Intel Group must upgrade to perfrom this action.'})
	if not 'groupids' in body:
		for groupid in tempids:
			subid = IntelGroups.objects.filter(id=groupid).last().plan_id
			if subid != None:
				planid = Subscription.objects.filter(djstripe_id=subid).last().plan_id
				productid = Plan.objects.filter(djstripe_id=planid).last().product_id
				custom_feeds = Product.objects.filter(djstripe_id=productid).last().metadata['custom_feeds']
				api_access = Product.objects.filter(djstripe_id=productid).last().metadata['api_access']
				current_period_end = Subscription.objects.filter(djstripe_id=subid).last().current_period_end
				if api_access and custom_feeds and current_period_end.replace(tzinfo=None) > datetime.now():
					groupids.append(groupid)
	else:
		for group in IntelGroups.objects.filter(uniqueid__in=body['groupids'].split(',')):
			subid = IntelGroups.objects.filter(id=group.id).last().plan_id
			if group.plan_id != None:
				planid = Subscription.objects.filter(djstripe_id=group.plan_id).last().plan_id
				productid = Plan.objects.filter(djstripe_id=planid).last().product_id
				custom_feeds = Product.objects.filter(djstripe_id=productid).last().metadata['custom_feeds']
				api_access = Product.objects.filter(djstripe_id=productid).last().metadata['api_access']
				current_period_end = Subscription.objects.filter(djstripe_id=subid).last().current_period_end
				if api_access and custom_feeds and current_period_end.replace(tzinfo=None) > datetime.now():
					for groupid in tempids:
						if int(groupid) == group.id:
							groupids.append(group.id)
	if not 'confidence' in body:
		if not 'category' in body:
			if not 'tags' in body:
				if not 'created_at' in body:
					if not 'updated_at' in body:
						feeds = GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True).order_by('id').all()
					else:
						feeds = GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, updated_at__date__gte=body['updated_at']).order_by('id').all()
				else:
					if not 'updated_at' in body:
						feeds = GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, created_at__date__gte=body['created_at']).order_by('id').all()
					else:
						feeds = GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, updated_at__date__gte=body['updated_at'], created_at__date__gte=body['created_at']).order_by('id').all()
			else:
				if not 'created_at' in body:
					if not 'updated_at' in body:
						tags = body['tags'].split(',')
						temp = []
						feeds = []
						flag = True
						for tag in tags:
							temp = temp + list(GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, tags__contains=tag.strip()).order_by('id').all())
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
							temp = temp + list(GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, tags__contains=tag.strip(), updated_at__date__gte=body['updated_at']).order_by('id').all())
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
							temp = temp + list(GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, tags__contains=tag.strip(), created_at__date__gte=body['created_at']).order_by('id').all())
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
							temp = temp + list(GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, tags__contains=tag.strip(), created_at__date__gte=body['created_at'], updated_at__date__gte=body['updated_at']).order_by('id').all())
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
						feeds = GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, category_id=body['category']).order_by('id').all()
					else:
						feeds = GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, category_id=body['category'], updated_at__date__gte=body['updated_at']).order_by('id').all()
				else:
					if not 'updated_at' in body:
						feeds = GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, category_id=body['category'], created_at__date__gte=body['created_at']).order_by('id').all()
					else:
						feeds = GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, category_id=body['category'], created_at__date__gte=body['created_at'], updated_at__date__gte=body['updated_at']).order_by('id').all()
			else:
				if not 'created_at' in body:
					if not 'updated_at' in body:
						tags = body['tags'].split(',')
						temp = []
						feeds = []
						flag = True
						for tag in tags:
							temp = temp + list(GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, category_id=body['category'], tags__contains=tag.strip()).order_by('id').all())
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
							temp = temp + list(GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, category_id=body['category'], tags__contains=tag.strip(), updated_at__date__gte=body['updated_at']).order_by('id').all())
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
							temp = temp + list(GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, category_id=body['category'], tags__contains=tag.strip(), created_at__date__gte=body['created_at']).order_by('id').all())
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
							temp = temp + list(GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, category_id=body['category'], tags__contains=tag.strip(), created_at__date__gte=body['created_at'], updated_at__date__gte=body['updated_at']).order_by('id').all())
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
						feeds = GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, confidence__gte=body['confidence']).order_by('id').all()
					else:
						feeds = GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, confidence__gte=body['confidence'], updated_at__date__gte=body['updated_at']).order_by('id').all()
				else:
					if not 'updated_at' in body:
						feeds = GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, confidence__gte=body['confidence'], created_at__date__gte=body['created_at']).order_by('id').all()
					else:
						feeds = GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, confidence__gte=body['confidence'], created_at__date__gte=body['created_at'], updated_at__date__gte=body['updated_at']).order_by('id').all()
			else:
				if not 'created_at' in body:
					if not 'updated_at' in body:
						tags = body['tags'].split(',')
						temp = []
						feeds = []
						flag = True
						for tag in tags:
							temp = temp + list(GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, confidence__gte=body['confidence'], tags__contains=tag.strip()).order_by('id').all())
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
							temp = temp + list(GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, confidence__gte=body['confidence'], updated_at__date__gte=body['updated_at'], tags__contains=tag.strip()).order_by('id').all())
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
							temp = temp + list(GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, confidence__gte=body['confidence'], created_at__date__gte=['created_at'], tags__contains=tag.strip()).order_by('id').all())
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
							temp = temp + list(GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, confidence__gte=body['confidence'], created_at__date__gte=['created_at'], updated_at__date__gte=['updated_at'], tags__contains=tag.strip()).order_by('id').all())
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
						feeds = GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, confidence__gte=body['confidence'], category_id=body['category']).order_by('id').all()
					else:
						feeds = GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, confidence__gte=body['confidence'], category_id=body['category'], updated_at__date__gte=body['updated_at']).order_by('id').all()
				else:
					if not 'updated_at' in body:
						feeds = GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, confidence__gte=body['confidence'], category_id=body['category'], created_at__date__gte=body['created_at']).order_by('id').all()
					else:
						feeds = GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, confidence__gte=body['confidence'], category_id=body['category'], created_at__date__gte=body['created_at'], updated_at__date__gte=body['updated_at']).order_by('id').all()
			else:
				if not 'created_at' in body:
					if not 'updated_at' in body:
						tags = body['tags'].split(',')
						temp = []
						feeds = []
						flag = True
						for tag in tags:
							temp = temp + list(GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, confidence__gte=body['confidence'], category_id=body['category'], tags__contains=tag.strip()).order_by('id').all())
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
							temp = temp + list(GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, confidence__gte=body['confidence'], category_id=body['category'], updated_at__date__gte=body['updated_at'], tags__contains=tag.strip()).order_by('id').all())
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
							temp = temp + list(GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, confidence__gte=body['confidence'], category_id=body['category'], created_at__date__gte=body['created_at'], tags__contains=tag.strip()).order_by('id').all())
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
							temp = temp + list(GroupFeeds.objects.filter(intelgroup_id__in=groupids, isenable=True, confidence__gte=body['confidence'], category_id=body['category'], created_at__date__gte=body['created_at'], updated_at__date__gte=body['updated_at'], tags__contains=tag.strip()).order_by('id').all())
						for t in temp:
							for feed in feeds:
								if(feed.id == t.id):
									flag = False
							if flag:
								feeds.append(t)
	result = []
	for feed in feeds:
		data = {
			'UUID': feed.uniqueid,
			'Type': feed.feed.type,
			'Feed_name': feed.name,
			'Feed_description': feed.description,
			'Feed_URL': feed.feed.url,
			'Intel_Group_UUID': feed.intelgroup.uniqueid,
			'Confidence': feed.confidence,
			'Category': feed.category.name,
			'Tags': feed.tags,
			'Datetime_created': feed.created_at,
			'Datetime_last_polled': feed.updated_at,
			'Dateteim_last_data': feed.updated_at,
			'RSS': FeedChannelSerializer(FeedChannels.objects.filter(feed_id=feed.feed.id).last()).data
		}
		result.append(data)
	return render(request, 'project/feeds.html', {'feeds':result})


uuid = openapi.Parameter('UUID', openapi.IN_QUERY, description="Intel Report UUID", type=openapi.TYPE_STRING)
groupids = openapi.Parameter('groupids', openapi.IN_QUERY, description="Intel Group UUIDs", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING))
channelids = openapi.Parameter('channelids', openapi.IN_QUERY, description="Feed Channel UUIDs", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING))
indicators = openapi.Parameter('indicators', openapi.IN_QUERY, description="Global Indicators", type=openapi.TYPE_STRING)
threattype = openapi.Parameter('threat_type', openapi.IN_QUERY, description="Attributes", type=openapi.TYPE_STRING)
threatactor = openapi.Parameter('threat_actor', openapi.IN_QUERY, description="Attributes", type=openapi.TYPE_STRING)
product = openapi.Parameter('product', openapi.IN_QUERY, description="Attributes", type=openapi.TYPE_STRING)
country = openapi.Parameter('country', openapi.IN_QUERY, description="Attributes", type=openapi.TYPE_STRING)
sector = openapi.Parameter('sector', openapi.IN_QUERY, description="Attributes", type=openapi.TYPE_STRING)
created_at = openapi.Parameter('created_at', openapi.IN_QUERY, description="Feed created_at(eg:2020-02-03)", type=openapi.TYPE_STRING)
updated_at = openapi.Parameter('updated_at', openapi.IN_QUERY, description="Feed updated_at(eg:2020-02-03)", type=openapi.TYPE_STRING)
@csrf_exempt
@swagger_auto_schema(methods=['get'], manual_parameters=[uuid, groupids, channelids, indicators, threattype, threatactor, product, country, sector, created_at, updated_at], responses={200: APIReportSerializer(many=True)})
@api_view(['GET'])
def apireports(request):
	if request.method == 'POST':
		body_unicode = request.body.decode('utf-8')
		body = json.loads(body_unicode)
	elif request.method == 'GET':
		body = request.GET
	userid = 0
	groupids = []
	tempids = []
	reports = []
	for apikey in APIKeys.objects.all():
		if apikey.value == request.headers['x-api-key']:
			tempids = apikey.groupids.split(',')
		userid = apikey.user_id
	if userid == 0:
		return render(request, 'project/reports.html', {'reports':'This is invalid apikey.'})
	if 'UUID' in body:
		if len(IntelReports.objects.filter(uniqueid=body['UUID']).all()) == 0:
			return render(request, 'project/reports.html', {'reports':"The report doesn't exist."})
		else:
			subid = IntelGroups.objects.filter(id=IntelReports.objects.filter(uniqueid=body['UUID']).last().intelgroup_id).last().plan_id
			if subid == None:
				return render(request, 'project/reports.html', {'reports':'Your Intel Group must upgrade to perfrom this action.'})
			else:
				planid = Subscription.objects.filter(djstripe_id=subid).last().plan_id
				productid = Plan.objects.filter(djstripe_id=planid).last().product_id
				api_access = Product.objects.filter(djstripe_id=productid).last().metadata['api_access']
				current_period_end = Subscription.objects.filter(djstripe_id=subid).last().current_period_end
				if api_access and current_period_end.replace(tzinfo=None) > datetime.now():
					report = ItemFeedGroupReportSerializer(IntelReports.objects.filter(uniqueid=body['UUID']).last()).data
					ip=[]; system=[]; infrastructure=[]; analysis=[]; hash=[]
					for indicator in GlobalItemIndicatorSerializer(Indicators.objects.filter(feeditem_id=report['feeditem']['id'], isenable=True).all(), many=True).data:
						if indicator['globalindicator']['type'] == 'IP':
							dic = {}
							dic[indicator['globalindicator']['value']] = indicator['value']
							ip.append(dic)
						elif indicator['globalindicator']['type'] == 'System':
							dic = {}
							dic[indicator['globalindicator']['value']] = indicator['value']
							system.append(dic)
						elif indicator['globalindicator']['type'] == 'Infrastructure':
							dic = {}
							dic[indicator['globalindicator']['value']] = indicator['value']
							infrastructure.append(dic)
						elif indicator['globalindicator']['type'] == 'Analysis':
							dic = {}
							dic[indicator['globalindicator']['value']] = indicator['value']
							analysis.append(dic)
						elif indicator['globalindicator']['type'] == 'Hash':
							dic = {}
							dic[indicator['globalindicator']['value']] = indicator['value']
							hash.append(dic)
					gthreattype=[]; gthreatactor=[]; gcountry=[]; gproduct=[]; gsector=[]
					for globalattribute in GroupGlobalAttributeSerializer(GroupGlobalAttributes.objects.filter(intelgroup_id=report['intelgroup']['id'], isenable=True), many=True).data:
						if globalattribute['globalattribute']['attribute'] == 'Threat type':
							dic = {}
							dic[globalattribute['globalattribute']['value']] = globalattribute['globalattribute']['words_matched']
							gthreattype.append(dic)
						elif globalattribute['globalattribute']['attribute'] == 'Threat actor':
							dic = {}
							dic[globalattribute['globalattribute']['value']] = globalattribute['globalattribute']['words_matched']
							gthreatactor.append(dic)
						elif globalattribute['globalattribute']['attribute'] == 'Country':
							dic = {}
							dic[globalattribute['globalattribute']['value']] = globalattribute['globalattribute']['words_matched']
							gcountry.append(dic)
						elif globalattribute['globalattribute']['attribute'] == 'Product':
							dic = {}
							dic[globalattribute['globalattribute']['value']] = globalattribute['globalattribute']['words_matched']
							gproduct.append(dic)
						elif globalattribute['globalattribute']['attribute'] == 'Sector':
							dic = {}
							dic[globalattribute['globalattribute']['value']] = globalattribute['globalattribute']['words_matched']
							gsector.append(dic)
					gattributes = {}
					if len(gthreattype) > 0:
						gattributes['Threat_type'] = gthreattype
					if len(gthreatactor) > 0:
						gattributes['Threat_actor'] = gthreatactor
					if len(gcountry) > 0:
						gattributes['Country'] = gcountry
					if len(gproduct) > 0:
						gattributes['Product'] = gproduct
					if len(gsector) > 0:
						gattributes['Sector'] = gsector
					threattype=[]; threatactor=[]; country=[]; product=[]; sector=[]
					for attribute in UserGroupAttributeSerializer(Attributes.objects.filter(intelgroup_id=report['intelgroup']['id'], isenable=True), many=True).data:
						if attribute['attribute'] == 'Threat type':
							dic = {}
							dic[attribute['value']] = attribute['words_matched']
							threattype.append(dic)
						elif attribute['attribute'] == 'Threat actor':
							dic = {}
							dic[attribute['value']] = attribute['words_matched']
							threatactor.append(dic)
						elif attribute['attribute'] == 'Country':
							dic = {}
							dic[attribute['value']] = attribute['words_matched']
							country.append(dic)
						elif attribute['attribute'] == 'Product':
							dic = {}
							dic[attribute['value']] = attribute['words_matched']
							product.append(dic)
						elif attribute['attribute'] == 'Sector':
							dic = {}
							dic[attribute['value']] = attribute['words_matched']
							sector.append(dic)
					attributes = {}
					if len(threattype) > 0:
						attributes['Threat_type'] = threattype
					if len(threatactor) > 0:
						attributes['Threat_actor'] = threatactor
					if len(country) > 0:
						attributes['Country'] = country
					if len(product) > 0:
						attributes['Product'] = product
					if len(sector) > 0:
						attributes['Sector'] = sector
					data = {
						'UUID':report['feeditem']['uniqueid'],
						'Channel_UUID':FeedChannelSerializer(FeedChannels.objects.filter(feed_id=report['feeditem']['feed']['id']).last()).data['uniqueid'],
						'Intel_Group_UUID':report['intelgroup']['uniqueid'],
						'Report_URL':f'{settings.SITE_ROOT_URL}/home/intelreports/'+str(report['id']),
						'Datetime_added':report['created_at'],
						'RSS_data':{
							'Title':report['feeditem']['title'],
							'Link':report['feeditem']['link'],
							'Description':json.dumps(report['feeditem']['description']),
							'Author':report['feeditem']['author'],
							'Category':report['feeditem']['category'],
							'Comments':report['feeditem']['comments'],
							'Enclosure':report['feeditem']['enclosure'],
							'Guid':report['feeditem']['guid'],
							'pubDate':report['feeditem']['pubdate'],
							'Source':report['feeditem']['source'],
						},
						'Indicators':{
							'IP':ip,
							'System':system,
							'Infrastructure':infrastructure,
							'Analysis':analysis,
							'Hash':hash
						},
						'Attributes':{
							'Global': gattributes,
							'Intel_Group': attributes
						}
					}
					return render(request, 'project/reports.html', {'reports':json.dumps(data)})
				else:
					return render(request, 'project/reports.html', {'reports':'Your Intel Group must upgrade to perfrom this action.'})
	if not 'groupids' in body:
		for groupid in tempids:
			subid = IntelGroups.objects.filter(id=groupid).last().plan_id
			if subid != None:
				planid = Subscription.objects.filter(djstripe_id=subid).last().plan_id
				productid = Plan.objects.filter(djstripe_id=planid).last().product_id
				custom_feeds = Product.objects.filter(djstripe_id=productid).last().metadata['custom_feeds']
				api_access = Product.objects.filter(djstripe_id=productid).last().metadata['api_access']
				current_period_end = Subscription.objects.filter(djstripe_id=subid).last().current_period_end
				if api_access and custom_feeds and current_period_end.replace(tzinfo=None) > datetime.now():
					groupids.append(groupid)
	else:
		for group in IntelGroups.objects.filter(uniqueid__in=body['groupids'].split(',')):
			subid = IntelGroups.objects.filter(id=group.id).last().plan_id
			if group.plan_id != None:
				planid = Subscription.objects.filter(djstripe_id=group.plan_id).last().plan_id
				productid = Plan.objects.filter(djstripe_id=planid).last().product_id
				custom_feeds = Product.objects.filter(djstripe_id=productid).last().metadata['custom_feeds']
				api_access = Product.objects.filter(djstripe_id=productid).last().metadata['api_access']
				current_period_end = Subscription.objects.filter(djstripe_id=subid).last().current_period_end
				if api_access and custom_feeds and current_period_end.replace(tzinfo=None) > datetime.now():
					for groupid in tempids:
						if int(groupid) == group.id:
							groupids.append(group.id)
	
	temp = []
	for groupid in groupids:
		flag = False
		if 'threat_type' in body:
			if len(Attributes.objects.filter(intelgroup_id=groupid, api_value=body['threat_type'], isenable=True).all()) > 0:
				flag =True
			for globalattribute in  GroupGlobalAttributeSerializer(GroupGlobalAttributes.objects.filter(intelgroup_id=groupid).all(), many=True).data:
				if globalattribute['globalattribute']['api_value'] == body['threat_type']:
					flag = True
		if 'threat_actor' in body:
			if len(Attributes.objects.filter(intelgroup_id=groupid, api_value=body['threat_actor']).all()) > 0:
				flag =True
			for globalattribute in  GroupGlobalAttributeSerializer(GroupGlobalAttributes.objects.filter(intelgroup_id=groupid).all(), many=True).data:
				if globalattribute['globalattribute']['api_value'] == body['threat_actor']:
					flag = True
		if 'product' in body:
			if len(Attributes.objects.filter(intelgroup_id=groupid, api_value=body['product']).all()) > 0:
				flag =True
			for globalattribute in  GroupGlobalAttributeSerializer(GroupGlobalAttributes.objects.filter(intelgroup_id=groupid).all(), many=True).data:
				if globalattribute['globalattribute']['api_value'] == body['product']:
					flag = True
		if 'country' in body:
			if len(Attributes.objects.filter(intelgroup_id=groupid, api_value=body['country']).all()) > 0:
				flag =True
			for globalattribute in  GroupGlobalAttributeSerializer(GroupGlobalAttributes.objects.filter(intelgroup_id=groupid).all(), many=True).data:
				if globalattribute['globalattribute']['api_value'] == body['country']:
					flag = True
		if 'sector' in body:
			if len(Attributes.objects.filter(intelgroup_id=groupid, api_value=body['sector']).all()) > 0:
				flag =True
			for globalattribute in  GroupGlobalAttributeSerializer(GroupGlobalAttributes.objects.filter(intelgroup_id=groupid).all(), many=True).data:
				if globalattribute['globalattribute']['api_value'] == body['sector']:
					flag = True
		if flag:
			temp.append(groupid)
	if not temp == []:
		groupids.clear()
		groupids = temp
	if not 'channelids' in body:
		if not 'indicators' in body:
			if not 'created_at' in body:
				if not 'updated_at' in body:
					for report in ItemFeedGroupReportSerializer(IntelReports.objects.filter(intelgroup_id__in=groupids).order_by('id').all(), many=True).data:
						if report['groupfeed']['isenable']:
							reports.append(report)
				else:
					for report in ItemFeedGroupReportSerializer(IntelReports.objects.filter(intelgroup_id__in=groupids, updated_at__date__gte=body['updated_at']).order_by('id').all(), many=True).data:
						if report['groupfeed']['isenable']:
							reports.append(report)
			else:
				if not 'updated_at' in body:
					for report in ItemFeedGroupReportSerializer(IntelReports.objects.filter(intelgroup_id__in=groupids, created_at__date__gte=body['created_at']).order_by('id').all(), many=True).data:
						if report['groupfeed']['isenable']:
							reports.append(report)
				else:
					for report in ItemFeedGroupReportSerializer(IntelReports.objects.filter(intelgroup_id__in=groupids, updated_at__date__gte=body['updated_at'], created_at__date__gte=body['created_at']).order_by('id').all(), many=True).data:
						if report['groupfeed']['isenable']:
							reports.append(report)
		else:
			if not 'created_at' in body:
				if not 'updated_at' in body:
					for report in ItemFeedGroupReportSerializer(IntelReports.objects.filter(intelgroup_id__in=groupids).order_by('id').all(), many=True).data:
						if report['groupfeed']['isenable']:
							flag = False
							for indicator in body['indicators'].split(','):
								for globalindicator in IndicatorGlobalSerializer(Indicators.objects.filter(feeditem_id=report['feeditem']['id'], isenable=True).order_by('id').all(), many=True).data:
									if globalindicator['globalindicator']['value_api'] == indicator.strip():
										flag = True
							if flag:
								reports.append(report)
				else:
					for report in ItemFeedGroupReportSerializer(IntelReports.objects.filter(intelgroup_id__in=groupids, updated_at__date__gte=body['updated_at']).order_by('id').all(), many=True).data:
						if report['groupfeed']['isenable']:
							flag = False
							for indicator in body['indicators'].split(','):
								for globalindicator in IndicatorGlobalSerializer(Indicators.objects.filter(feeditem_id=report['feeditem']['id'], isenable=True).order_by('id').all(), many=True).data:
									if globalindicator['globalindicator']['value_api'] == indicator.strip():
										flag = True
							if flag:
								reports.append(report)

			else:
				if not 'updated_at' in body:
					for report in ItemFeedGroupReportSerializer(IntelReports.objects.filter(intelgroup_id__in=groupids, created_at__date__gte=body['created_at']).order_by('id').all(), many=True).data:
						if report['groupfeed']['isenable']:
							flag = False
							for indicator in body['indicators'].split(','):
								for globalindicator in IndicatorGlobalSerializer(Indicators.objects.filter(feeditem_id=report['feeditem']['id'], isenable=True).order_by('id').all(), many=True).data:
									if globalindicator['globalindicator']['value_api'] == indicator.strip():
										flag = True
							if flag:
								reports.append(report)
				else:
					for report in ItemFeedGroupReportSerializer(IntelReports.objects.filter(intelgroup_id__in=groupids, created_at__date__gte=body['created_at'], updated_at__date__gte=body['updated_at']).order_by('id').all(), many=True).data:
						if report['groupfeed']['isenable']:
							flag = False
							for indicator in body['indicators'].split(','):
								for globalindicator in IndicatorGlobalSerializer(Indicators.objects.filter(feeditem_id=report['feeditem']['id'], isenable=True).order_by('id').all(), many=True).data:
									if globalindicator['globalindicator']['value_api'] == indicator.strip():
										flag = True
							if flag:
								reports.append(report)
	else:
		if not 'indicators' in body:
			if not 'created_at' in body:
				if not 'updated_at' in body:
					for report in ItemFeedGroupReportSerializer(IntelReports.objects.filter(intelgroup_id__in=groupids).order_by('id').all(), many=True).data:
						if report['groupfeed']['isenable']:
							flag = False
							for channelid in body['channelids'].split(','):
								if report['feeditem']['feed']['id'] == FeedChannels.objects.filter(uniqueid=channelid).order_by('id').last().feed_id:
									flag = True
							if flag:
								reports.append(report)
				else:
					for report in ItemFeedGroupReportSerializer(IntelReports.objects.filter(intelgroup_id__in=groupids, updated_at__date__gte=body['updated_at']).order_by('id').all(), many=True).data:
						if report['groupfeed']['isenable']:
							flag = False
							for channelid in body['channelids'].split(','):
								if report['feeditem']['feed']['id'] == FeedChannels.objects.filter(uniqueid=channelid).order_by('id').last().feed_id:
									flag = True
							if flag:
								reports.append(report)
			else:
				if not 'updated_at' in body:
					for report in ItemFeedGroupReportSerializer(IntelReports.objects.filter(intelgroup_id__in=groupids, created_at__date__gte=body['created_at']).order_by('id').all(), many=True).data:
						if report['groupfeed']['isenable']:
							flag = False
							for channelid in body['channelids'].split(','):
								if report['feeditem']['feed']['id'] == FeedChannels.objects.filter(uniqueid=channelid).order_by('id').last().feed_id:
									flag = True
							if flag:
								reports.append(report)
				else:
					for report in ItemFeedGroupReportSerializer(IntelReports.objects.filter(intelgroup_id__in=groupids, created_at__date__gte=body['created_at'], updated_at__date__gte=body['updated_at']).order_by('id').all(), many=True).data:
						if report['groupfeed']['isenable']:
							flag = False
							for channelid in body['channelids'].split(','):
								if report['feeditem']['feed']['id'] == FeedChannels.objects.filter(uniqueid=channelid).order_by('id').last().feed_id:
									flag = True
							if flag:
								reports.append(report)
		else:
			if not 'created_at' in body:
				if not 'updated_at' in body:
					for report in ItemFeedGroupReportSerializer(IntelReports.objects.filter(intelgroup_id__in=groupids).order_by('id').all(), many=True).data:
						if report['groupfeed']['isenable']:
							flag = False
							for channelid in body['channelids'].split(','):
								if report['feeditem']['feed']['id'] == FeedChannels.objects.filter(uniqueid=channelid).order_by('id').last().feed_id:
									flag = True
							if flag:
								iflag = False
								for indicator in body['indicators'].split(','):
									for globalindicator in IndicatorGlobalSerializer(Indicators.objects.filter(feeditem_id=report['feeditem']['id'], isenable=True).order_by('id').all(), many=True).data:
										if globalindicator['globalindicator']['value_api'] == indicator.strip():
											iflag = True
								if iflag:
									reports.append(report)
				else:
					for report in ItemFeedGroupReportSerializer(IntelReports.objects.filter(intelgroup_id__in=groupids, updated_at__date__gte=body['updated_at']).order_by('id').all(), many=True).data:
						if report['groupfeed']['isenable']:
							flag = False
							for channelid in body['channelids'].split(','):
								if report['feeditem']['feed']['id'] == FeedChannels.objects.filter(uniqueid=channelid).order_by('id').last().feed_id:
									flag = True
							if flag:
								iflag = False
								for indicator in body['indicators'].split(','):
									for globalindicator in IndicatorGlobalSerializer(Indicators.objects.filter(feeditem_id=report['feeditem']['id'], isenable=True).order_by('id').all(), many=True).data:
										if globalindicator['globalindicator']['value_api'] == indicator.strip():
											iflag = True
								if iflag:
									reports.append(report)
			else:
				if not 'updated_at' in body:
					for report in ItemFeedGroupReportSerializer(IntelReports.objects.filter(intelgroup_id__in=groupids, created_at__date__gte=body['updated_at']).order_by('id').all(), many=True).data:
						if report['groupfeed']['isenable']:
							flag = False
							for channelid in body['channelids'].split(','):
								if report['feeditem']['feed']['id'] == FeedChannels.objects.filter(uniqueid=channelid).order_by('id').last().feed_id:
									flag = True
							if flag:
								iflag = False
								for indicator in body['indicators'].split(','):
									for globalindicator in IndicatorGlobalSerializer(Indicators.objects.filter(feeditem_id=report['feeditem']['id'], isenable=True).order_by('id').all(), many=True).data:
										if globalindicator['globalindicator']['value_api'] == indicator.strip():
											iflag = True
								if iflag:
									reports.append(report)
				else:
					for report in ItemFeedGroupReportSerializer(IntelReports.objects.filter(intelgroup_id__in=groupids, created_at__date__gte=body['updated_at'], updated_at__date__gte=body['updated_at']).order_by('id').all(), many=True).data:
						if report['groupfeed']['isenable']:
							flag = False
							for channelid in body['channelids'].split(','):
								if report['feeditem']['feed']['id'] == FeedChannels.objects.filter(uniqueid=channelid).order_by('id').last().feed_id:
									flag = True
							if flag:
								iflag = False
								for indicator in body['indicators'].split(','):
									for globalindicator in IndicatorGlobalSerializer(Indicators.objects.filter(feeditem_id=report['feeditem']['id'], isenable=True).order_by('id').all(), many=True).data:
										if globalindicator['globalindicator']['value_api'] == indicator.strip():
											iflag = True
								if iflag:
									reports.append(report)
	
	result = []
	for report in reports:
		ip=[], system=[], infrastructure=[], analysis=[], hash=[]
		for indicator in GlobalItemIndicatorSerializer(Indicators.objects.filter(feeditem_id=report['feeditem']['id'], isenable=True).all(), many=True).data:
			if indicator['globalindicator']['type'] == 'IP':
				dic = {}
				dic[indicator['globalindicator']['value']] = indicator['value']
				ip.append(dic)
			elif indicator['globalindicator']['type'] == 'System':
				dic = {}
				dic[indicator['globalindicator']['value']] = indicator['value']
				system.append(dic)
			elif indicator['globalindicator']['type'] == 'Infrastructure':
				dic = {}
				dic[indicator['globalindicator']['value']] = indicator['value']
				infrastructure.append(dic)
			elif indicator['globalindicator']['type'] == 'Analysis':
				dic = {}
				dic[indicator['globalindicator']['value']] = indicator['value']
				analysis.append(dic)
			elif indicator['globalindicator']['type'] == 'Hash':
				dic = {}
				dic[indicator['globalindicator']['value']] = indicator['value']
				hash.append(dic)
		gthreattype=[]; gthreatactor=[]; gcountry=[]; gproduct=[]; gsector=[]
		for globalattribute in GroupGlobalAttributeSerializer(GroupGlobalAttributes.objects.filter(intelgroup_id=report['intelgroup']['id'], isenable=True), many=True).data:
			if globalattribute['globalattribute']['attribute'] == 'Threat type':
				dic = {}
				dic[globalattribute['globalattribute']['value']] = globalattribute['globalattribute']['words_matched']
				gthreattype.append(dic)
			elif globalattribute['globalattribute']['attribute'] == 'Threat actor':
				dic = {}
				dic[globalattribute['globalattribute']['value']] = globalattribute['globalattribute']['words_matched']
				gthreatactor.append(dic)
			elif globalattribute['globalattribute']['attribute'] == 'Country':
				dic = {}
				dic[globalattribute['globalattribute']['value']] = globalattribute['globalattribute']['words_matched']
				gcountry.append(dic)
			elif globalattribute['globalattribute']['attribute'] == 'Product':
				dic = {}
				dic[globalattribute['globalattribute']['value']] = globalattribute['globalattribute']['words_matched']
				gproduct.append(dic)
			elif globalattribute['globalattribute']['attribute'] == 'Sector':
				dic = {}
				dic[globalattribute['globalattribute']['value']] = globalattribute['globalattribute']['words_matched']
				gsector.append(dic)
		gattributes = {}
		if len(gthreattype) > 0:
			gattributes['Threat_type'] = gthreattype
		if len(gthreatactor) > 0:
			gattributes['Threat_actor'] = gthreatactor
		if len(gcountry) > 0:
			gattributes['Country'] = gcountry
		if len(gproduct) > 0:
			gattributes['Product'] = gproduct
		if len(gsector) > 0:
			gattributes['Sector'] = gsector
		threattype=[]; threatactor=[]; country=[]; product=[]; sector=[]
		for attribute in UserGroupAttributeSerializer(Attributes.objects.filter(intelgroup_id=report['intelgroup']['id'], isenable=True), many=True).data:
			if attribute['attribute'] == 'Threat type':
				dic = {}
				dic[attribute['value']] = attribute['words_matched']
				threattype.append(dic)
			elif attribute['attribute'] == 'Threat actor':
				dic = {}
				dic[attribute['value']] = attribute['words_matched']
				threatactor.append(dic)
			elif attribute['attribute'] == 'Country':
				dic = {}
				dic[attribute['value']] = attribute['words_matched']
				country.append(dic)
			elif attribute['attribute'] == 'Product':
				dic = {}
				dic[attribute['value']] = attribute['words_matched']
				product.append(dic)
			elif attribute['attribute'] == 'Sector':
				dic = {}
				dic[attribute['value']] = attribute['words_matched']
				sector.append(dic)
		attributes = {}
		if len(threattype) > 0:
			attributes['Threat_type'] = threattype
		if len(threatactor) > 0:
			attributes['Threat_actor'] = threatactor
		if len(country) > 0:
			attributes['Country'] = country
		if len(product) > 0:
			attributes['Product'] = product
		if len(sector) > 0:
			attributes['Sector'] = sector
		data = {
			'UUID':report['feeditem']['uniqueid'],
			'Channel_UUID':FeedChannels.objects.filter(feed_id=report['feeditem']['feed']['id']).last().uniqueid,
			'Intel_Group_UUID':report['intelgroup']['uniqueid'],
			'Report_URL':f'{settings.SITE_ROOT_URL}/home/intelreports/'+str(report['id']),
			'Datetime_added':report['created_at'],
			'RSS_data':{
				'Title':report['feeditem']['title'],
				'Link':report['feeditem']['link'],
				'Description':report['feeditem']['description'],
				'Author':report['feeditem']['author'],
				'Category':report['feeditem']['category'],
				'Comments':report['feeditem']['comments'],
				'Enclosure':report['feeditem']['enclosure'],
				'Guid':report['feeditem']['guid'],
				'pubDate':report['feeditem']['pubdate'],
				'Source':report['feeditem']['source'],
			},
			'Indicators':{
				'IP':ip,
				'System':system,
				'Infrastructure':infrastructure,
				'Analysis':analysis,
				'Hash':hash
			},
			'Attributes':{
				'Global': gattributes,
				'Intel_Group': attributes
			}
		}
		result.append(data)
	return render(request, 'project/reports.html', {'reports':result})

@csrf_exempt
@swagger_auto_schema(methods=['get'], responses={200: APIGroupSerializer(many=True)})
@api_view(['GET'])
def apigroups(request):
	groupids = []
	tempids = []
	userid = 0
	for apikey in APIKeys.objects.all():
		if apikey.value == request.headers['x-api-key']:
			tempids = apikey.groupids.split(',')
			userid = apikey.user_id
	if userid == 0:
		return render(request, 'project/intel_groups.html', {'groups':'This is invalid apikey.'})
	for groupid in tempids:
		subid = IntelGroups.objects.filter(id=groupid).last().plan_id
		if subid != None:
			planid = Subscription.objects.filter(djstripe_id=subid).last().plan_id
			productid = Plan.objects.filter(djstripe_id=planid).last().product_id
			custom_feeds = Product.objects.filter(djstripe_id=productid).last().metadata['custom_feeds']
			current_period_end = Subscription.objects.filter(djstripe_id=subid).last().current_period_end
			if custom_feeds and current_period_end.replace(tzinfo=None) > datetime.now():
				groupids.append(groupid)
	result = []
	for groupid in groupids:	
		data = {
			'UUID': IntelGroups.objects.filter(id=groupid).last().uniqueid,
			'Name': IntelGroups.objects.filter(id=groupid).last().name,
			'Description': IntelGroups.objects.filter(id=groupid).last().description,
			'Role': UserIntelGroupRoles.objects.filter(intelgroup_id=groupid, user_id=userid).last().role
		}
		result.append(data)
	return render(request, 'project/intel_groups.html', {'groups':result})

@api_view(['POST'])
@permission_classes([AllowAny])
def webhook(request):
	endpoint_secret = settings.DJSTRIPE_WEBHOOK_SECRET
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
	profile = UserSerializer(CustomUser.objects.filter(id=request.user.id).last()).data
	intelgroups = RoleGroupSerializer(UserIntelGroupRoles.objects.filter(user_id=request.user.id).order_by('intelgroup_id').all(), many=True).data
	apikeys = APIkeySerializer(APIKeys.objects.filter(user_id=request.user.id).order_by('id').all(), many=True).data
	webhooks = GroupWebHookSerializer(WebHooks.objects.filter(user_id=request.user.id).order_by('id').all(), many=True).data
	return Response({'profile':profile, 'intelgroups':intelgroups, 'apikeys':apikeys, 'webhooks':webhooks});

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

@swagger_auto_schema(methods=['post'], request_body=APIKeyCreateSerializer, responses={201: APIkeySerializer(many=True)})
@swagger_auto_schema(methods=['delete'], request_body=IDSerializer, responses={204: APIkeySerializer(many=True)})
@api_view(['POST', 'DELETE'])
def apikeys(request):
	if request.method == 'POST':
		key = secrets.token_urlsafe(16)
		groupids = []
		for role in UserIntelGroupRoles.objects.filter(user_id=request.user.id).exclude(role=0).all():
			groupids.append(role.intelgroup_id)
		APIKeys.objects.create(name=request.data['name'], groupids=','.join(str(groupid) for groupid in groupids), value=key, user_id=request.user.id)
		apikeys = APIkeySerializer(APIKeys.objects.filter(user_id=request.user.id).all(), many=True).data
		return Response(apikeys)
	elif request.method == 'DELETE':
		APIKeys.objects.filter(id=request.data['id']).delete()
		apikeys = APIkeySerializer(APIKeys.objects.filter(user_id=request.user.id).all(), many=True).data
		return Response(apikeys)

@swagger_auto_schema(methods=['post'], request_body=WebhookCreateSerializer, responses={201: GroupWebHookSerializer(many=True)})
@swagger_auto_schema(methods=['put'], request_body=WebhookUpdateSerializer, responses={200: GroupWebHookSerializer(many=True)})
@swagger_auto_schema(methods=['delete'], request_body=IDSerializer, responses={204: GroupWebHookSerializer(many=True)})
@api_view(['POST', 'PUT', 'DELETE'])
def webhooks(request):
	if request.method == 'POST':
		WebHooks.objects.create(endpoint=request.data['endpoint'], description=request.data['description'], intelgroup_id=request.data['intelgroup_id'], user_id=request.user.id, words=request.data['words'])
		webhooks = GroupWebHookSerializer(webhook in WebHooks.objects.filter(user_id=request.user.id).all(), many=True).data
		return Response(webhooks)
	elif request.method == 'PUT':
		WebHooks.objects.filter(id=request.data['id']).update(endpoint=request.data['endpoint'], description=request.data['description'], intelgroup_id=request.data['intelgroup_id'], words=request.data['words'], user_id=request.user.id, isenable=request.data['isenable'])
		webhooks = GroupWebHookSerializer(WebHooks.objects.filter(user_id=request.user.id).all(), many=True).data
		return Response(webhooks)
	elif request.method == 'DELETE':
		WebHooks.objects.filter(id=request.data['id']).delete()
		webhooks = GroupWebHookSerializer(WebHooks.objects.filter(user_id=request.user.id).all(), many=True).data
		return Response(webhooks)

@swagger_auto_schema(methods=['post'], request_body=IDSerializer, responses={201: ItemFeedGroupReportSerializer})
@api_view(['POST'])
def reports(request):
	if request.data['id'] == '':
		groupid = UserIntelGroupRoles.objects.filter(id=request.user.id).order_by('intelgroup_id').last().intelgroup_id
	else:
		groupid = request.data['id']
	itemids = []
	groupfeeds = GroupCategoryFeedSerializer(GroupFeeds.objects.filter(intelgroup_id=groupid).all(), many=True)
	for report in IntelReports.objects.filter(intelgroup_id=groupid).order_by('id').all():
		itemids.append(report.feeditem_id)
	indicators = []
	for indicator in ItemIndicatorSerializer(Indicators.objects.filter(feeditem_id__in=itemids, isenable=True).order_by('id').all(), many=True).data:
		if len(UserIndicatorWhitelistSerializer(Whitelists.objects.filter(enabled="Enable").order_by('id').all(), many=True).data) >0:
			for white in UserIndicatorWhitelistSerializer(Whitelists.objects.filter(enabled="Enable").order_by('id').all(), many=True).data:
				flag = True
				if indicator['globalindicator_id'] == white['globalindicator_id'] and white['value'] in indicator['value']:
					flag = False
				if flag:
					indicators.append(indicator)
		else:
			indicators.append(indicator)
	extractions = UserGroupAttributeSerializer(Attributes.objects.filter(intelgroup_id=groupid, isenable=True).order_by('id').all(), many=True)
	categories = CategorySerializer(Categories.objects.order_by('id').all(), many=True)
	tags = TagSerializer(Tags.objects.filter(Q(isglobal=True) | Q(intelgroup_id=groupid)).order_by('id').all(), many=True)
	globalindicators = GlobalIndicatorSerializer(GlobalIndicators.objects.order_by('id').all(), many=True)
	reports = []
	for report in IntelReports.objects.filter(intelgroup_id=groupid).order_by('id').all():
		serializer = ItemFeedGroupReportSerializer(report)
		if serializer.data['groupfeed']['isenable']:
			reports.append(serializer.data)
	globalattributes = GroupGlobalAttributeSerializer(GroupGlobalAttributes.objects.filter(intelgroup_id=groupid, isenable=True), many=True)
	return Response({'feeds':groupfeeds.data, 'indicators':indicators, 'extractions':extractions.data, 'categories':categories.data, 'tags':tags.data, 'globalindicators':globalindicators.data, 'reports':reports, 'globalattributes':globalattributes.data})

@swagger_auto_schema(methods=['post'], request_body=SearchReportSerializer, responses={201: FeedCategorySerializer})
@api_view(['POST'])
def searchreports(request):
	itemids = []
	reports = []
	if request.data['classification'] == '0':
		if request.data['indicator'] == '0':
			if request.data['category'] == '0':
				if request.data['tag'] == '0':
					if request.data['confidence'] == '0':
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable']:
									reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and serializer.data['groupfeed']['id'] == int(request.data['feedname']):
									reports.append(serializer.data)
					else:
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']):
									reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and int(request.data['feedname']) == serializer.data['groupfeed']['id'] and serializer.data['groupfeed']['confidence'] >= request.data['confidence']:
									reports.append(serializer.data)
				else:
					if request.data['confidence'] == '0':
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and request.data['tag'] in serializer.data['groupfeed']['tags']:
									reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and request.data['tag'] in serializer.data['groupfeed']['tags'] and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
									reports.append(serializer.data)
					else:
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and request.data['tag'] in serializer.data['groupfeed']['tags'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']):
									reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and request.data['tag'] in serializer.data['groupfeed']['tags'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']) and request.data['feedname'] == serializer.data['groupfeed']['name']:
									reports.append(serializer.data)
			else:
				if request.data['tag'] == '0':
					if request.data['confidence'] == '0':
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and int(request.data['category']) == serializer.data['groupfeed']['category']['id']:
									reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
									reports.append(serializer.data)
					else:
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']):
									reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']) and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
									reports.append(serializer.data)
				else:
					if request.data['confidence'] == '0':
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and request.data['tag'] in serializer.data['groupfeed']['tags']:
									reports.append(serializer.data)								
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and request.data['tag'] in serializer.data['groupfeed']['tags'] and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
									reports.append(serializer.data)
					else:
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and request.data['tag'] in serializer.data['groupfeed']['tags'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']):
									reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and request.data['tag'] in serializer.data['groupfeed']['tags'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']) and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
									reports.append(serializer.data)
		else:
			if request.data['category'] == '0':
				if request.data['tag'] == '0':
					if request.data['confidence'] == '0':
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0:
									reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
									reports.append(serializer.data)
					else:
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']):
									reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']) and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
									reports.append(serializer.data)
				else:
					if request.data['confidence'] == '0':
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and request.data['tag'] in serializer.data['groupfeed']['tags']:
									reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and request.data['tag'] in serializer.data['groupfeed']['tags'] and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
									reports.append(serializer.data)
					else:
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and request.data['tag'] in serializer.data['groupfeed']['tags'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']):
									reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and request.data['tag'] in serializer.data['groupfeed']['tags'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']) and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
									reports.append(serializer.data)
			else:
				if request.data['tag'] == '0':
					if request.data['confidence'] == '0':
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and int(request.data['category']) == serializer.data['groupfeed']['category']['id']:
									reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
									reports.append(serializer.data)
					else:
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']):
									reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']) and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
									reports.append(serializer.data)
				else:
					if request.data['confidence'] == '0':
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and request.data['tag'] in serializer.data['groupfeed']['tags']:
									reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and request.data['tag'] in serializer.data['groupfeed']['tags'] and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
									reports.append(serializer.data)								
					else:
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and request.data['tag'] in serializer.data['groupfeed']['tags'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']):
									reports.append(serializer.data)
								
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and request.data['tag'] in serializer.data['groupfeed']['tags'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']) and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
									reports.append(serializer.data)
	else:
		if request.data['indicator'] == '0':
			if request.data['category'] == '0':
				if request.data['tag'] == '0':
					if request.data['confidence'] == '0':
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if int(request.data['feedname']) == serializer.data['groupfeed']['id']:
										reports.append(serializer.data)
					else:
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']):
										reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if int(request.data['feedname']) == serializer.data['groupfeed']['id'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']):
										reports.append(serializer.data)
				else:
					if request.data['confidence'] == '0':
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if request.data['tag'] in serializer.data['groupfeed']['tags']:
										reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if request.data['tag'] in serializer.data['groupfeed']['tags'] and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
										reports.append(serializer.data)
					else:
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if request.data['tag'] in serializer.data['groupfeed']['tags'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']):
										reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if request.data['tag'] in serializer.data['groupfeed']['tags'] and int(request.data['feedname']) == serializer.data['groupfeed']['id'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']):
										reports.append(serializer.data)
			else:
				if request.data['tag'] == '0':
					if request.data['confidence'] == '0':
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if int(request.data['category']) == serializer.data['groupfeed']['category']['id']:
										reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
										reports.append(serializer.data)
					else:
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']):
										reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']) and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
										reports.append(serializer.data)
				else:
					if request.data['confidence'] == '0':
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and request.data['tag'] in serializer.data['groupfeed']['tags']:
										reports.append(serializer.data)
								
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and request.data['tag'] in serializer.data['groupfeed']['tags'] and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
										reports.append(serializer.data)
					else:
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and request.data['tag'] in serializer.data['groupfeed']['tags'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']):
										reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and request.data['tag'] in serializer.data['groupfeed']['tags'] and int(request.data['feedname']) == serializer.data['groupfeed']['id'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']):
										reports.append(serializer.data)
		else:
			if request.data['category'] == '0':
				if request.data['tag'] == '0':
					if request.data['confidence'] == '0':
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0:
										reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
									reports.append(serializer.data)
								
					else:
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']):
										reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']) and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
										reports.append(serializer.data)
				else:
					if request.data['confidence'] == '0':
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and request.data['tag'] in serializer.data['groupfeed']['tags']:
										reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and request.data['tag'] in serializer.data['groupfeed']['tags'] and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
										reports.append(serializer.data)
					else:
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and request.data['tag'] in serializer.data['groupfeed']['tags'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']):
										reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and request.data['tag'] in serializer.data['groupfeed']['tags'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']) and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
										reports.append(serializer.data)
			else:
				if request.data['tag'] == '0':
					if request.data['confidence'] == '0':
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and int(request.data['category']) == serializer.data['groupfeed']['category']['id']:
										reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
										reports.append(serializer.data)
					else:
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']):
										reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']) and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
										reports.append(serializer.data)
				else:
					if request.data['confidence'] == '0':
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and request.data['tag'] in serializer.data['groupfeed']['tags']:
										reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and request.data['tag'] in serializer.data['groupfeed']['tags'] and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
										reports.append(serializer.data)
					else:
						if request.data['feedname'] == '0':
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and request.data['tag'] in serializer.data['groupfeed']['tags'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']):
										reports.append(serializer.data)
						else:
							for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
								serializer = ItemFeedGroupReportSerializer(report)
								if serializer.data['groupfeed']['isenable'] and len(Attributes.objects.filter(intelgroup_id=request.data['id'], words_matched__contains=request.data['classification'], isenable=True).all())>0 or (len(GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).all())>0 and GroupGlobalAttributes.objects.filter(globalattribute_id=GlobalAttributes.objects.filter(words_matched__contains=request.data['classification']).last().id).last().isenable):
									if len(Indicators.objects.filter(feeditem_id=report.feeditem_id, globalindicator_id=request.data['indicator']))>0 and int(request.data['category']) == serializer.data['groupfeed']['category']['id'] and request.data['tag'] in serializer.data['groupfeed']['tags'] and serializer.data['groupfeed']['confidence'] >= int(request.data['confidence']) and int(request.data['feedname']) == serializer.data['groupfeed']['id']:
										reports.append(serializer.data)
	results = []
	if request.data['intelligence'] == '':
		results = reports
	else:
		for report in reports:
			flag = False
			for indicator in Indicators.objects.filter(feeditem_id=report['feeditem']['id']).order_by('id').all():
				if request.data['intelligence'] in indicator.value:
					flag = True
			for attribute in Attributes.objects.filter(intelgroup_id=report['intelgroup']['id'], isenable=True).order_by('id').all():
				if request.data['intelligence'] in attribute.words_matched:
					flag = True
			for globalattribute in GroupGlobalAttributeSerializer(GroupGlobalAttributes.objects.filter(intelgroup_id=report['intelgroup']['id']).order_by('id').all(), many=True).data:
				if request.data['intelligence'] in globalattribute['globalattribute']['words_matched']:
					flag = True
			if flag:
				results.append(report)

	for report in IntelReports.objects.filter(intelgroup_id=request.data['id']).all():
		itemids.append(report.feeditem.id)
	indicators = []
	for indicator in ItemIndicatorSerializer(Indicators.objects.filter(feeditem_id__in=itemids, isenable=True).order_by('id').all(), many=True).data:
		if len(UserIndicatorWhitelistSerializer(Whitelists.objects.filter(enabled="Enable").order_by('id').all(), many=True).data) > 0:
			for white in UserIndicatorWhitelistSerializer(Whitelists.objects.filter(enabled="Enable").order_by('id').all(), many=True).data:
				flag = True
				if indicator['globalindicator_id'] == white['globalindicator_id'] and white['value'] in indicator['value']:
					flag = False
				if flag:
					indicators.append(indicator)
		else:
			indicators.append(indicator)
	extractions = Attributes.objects.filter(intelgroup_id=request.data['id'], isenable=True).order_by('id').all()
	extraction_serializer = UserGroupAttributeSerializer(extractions, many=True)
	categories = Categories.objects.order_by('id').all()
	category_serializer = CategorySerializer(categories, many=True)
	tags = Tags.objects.filter(Q(isglobal=True) | Q(intelgroup_id=request.user.id)).order_by('id').all()
	tag_serializer = TagSerializer(tags, many=True)
	globalindicators = GlobalIndicators.objects.order_by('id').all()
	global_serializer = GlobalIndicatorSerializer(globalindicators, many=True)

	return Response({'reports':results, 'indicators':indicators, 'extractions':extraction_serializer.data, 'categories':category_serializer.data, 'tags':tag_serializer.data, 'globalindicators':global_serializer.data})

@api_view(['POST'])
def pullfeed(request):
	if request.data['groupid'] == '':
		groupid = UserIntelGroupRoles.objects.filter(user_id=request.user.id).order_by('intelgroup_id').last().intelgroup_id
	else:
		groupid = request.data['groupid']
	isUrlExist = False
	for feed in Feeds.objects.all():
		if(request.data['url'] in feed.url):
			if len(GroupFeeds.objects.filter(feed_id=feed.id, intelgroup_id=groupid).all()) > 0:
				isUrlExist = True
				return Response({'isUrlExist':isUrlExist})
	if not isUrlExist:
		ftr = "http://ftr-premium.fivefilters.org/"
		encode = urllib.parse.quote_plus(request.data['url'])
		key = urllib.parse.quote_plus("KSF8GH22GZRKA8")
		req = urllib.request.Request(ftr+"makefulltextfeed.php?url="+encode+"&key="+key+"&max=25")
		contents = urllib.request.urlopen(req).read()
		results = []
		if type(xmltodict.parse(contents)['rss']['channel']['item']) == list:
			for item in xmltodict.parse(contents)['rss']['channel']['item']:
				data = []
				for indicator in extract.extract_observables(json.dumps(item)):
					if len(extract.extract_observables(json.dumps(item))[indicator]) > 0:
						data.append({'indicator':indicator, 'value':extract.extract_observables(json.dumps(item))[indicator]})
				if not data == []:
					results.append(data)
		else:
			item = xmltodict.parse(contents)['rss']['channel']['item']
			data = []
			for indicator in extract.extract_observables(json.dumps(item)):
				if len(extract.extract_observables(json.dumps(item))[indicator]) > 0:
					data.append({'indicator':indicator, 'value':extract.extract_observables(json.dumps(item))[indicator]})
			if not data == []:
				results.append(data)
		extractions = UserGroupAttributeSerializer(Attributes.objects.filter(intelgroup_id=groupid, isenable=True).order_by('id').all(), many=True).data
		globalattributes = GroupGlobalAttributeSerializer(GroupGlobalAttributes.objects.filter(intelgroup_id=groupid, isenable=True), many=True).data
		return Response({'fulltext':xmltodict.parse(contents), 'indicators':results, 'attributes':extractions, 'globalattributes':globalattributes, 'isUrlExist':isUrlExist})

@swagger_auto_schema(methods=['post'], request_body=FeedCreateSerializer, responses={201: FeedCategorySerializer})
@swagger_auto_schema(methods=['put'], request_body=FeedUpdateSerializer, responses={200: FeedCategorySerializer})
@api_view(['POST', 'PUT'])
def feeds(request):
	if request.method == 'POST':
		data=request.data
		tags = data['tags'].split(',')
		groupid= request.data['intelgroup_id']
		isUrlExist = False
		for feed in Feeds.objects.all():
			if(data['url'] in feed.url):
				if len(GroupFeeds.objects.filter(feed_id=feed.id, intelgroup_id=groupid).all()) > 0:
					isUrlExist = True
				else:
					if data['tags'] == '':
						GroupFeeds.objects.create(feed_id=feed.id, name=data['name'], description=data['description'], category_id=data['category'], tags=feed.tags, isenable=True, confidence=data['confidence'], intelgroup_id=groupid)
					else:
						GroupFeeds.objects.create(feed_id=feed.id, name=data['name'], description=data['description'], category_id=data['category'], tags=data['tags'], isenable=True, confidence=data['confidence'], intelgroup_id=groupid)
		if not isUrlExist:
			subid = IntelGroups.objects.filter(id=groupid).last().plan_id
			max_feeds = 0
			if not subid == None:
				planid = Subscription.objects.filter(djstripe_id=subid).last().plan_id
				productid = Plan.objects.filter(djstripe_id=planid).last().product_id
				max_feeds = Product.objects.filter(djstripe_id=productid).last().metadata['max_feeds']
				feeds = Feeds.objects.filter(intelgroup_id=groupid).all()
				if len(feeds) > int(max_feeds):
					return Response({'message':True, 'isUrlExist':isUrlExist})
			Feeds.objects.create(type=data['type'], url=data['url'], name=data['name'], description=data['description'], category_id=data['category'], tags=data['tags'], isglobal=False, confidence=data['confidence'], intelgroup_id=groupid)
			GroupFeeds.objects.create(feed_id=Feeds.objects.last().id, intelgroup_id=groupid, name=data['name'], description=data['description'], category_id=data['category'], tags=data['tags'], confidence=data['confidence'], isenable=True)
			for tag in tags:
				flag = False
				for existingtag in Tags.objects.all():
					if tag.strip() == existingtag.name:
						flag = True
				if not flag:
					if request.user.is_staff:
						Tags.objects.create(name=tag.strip(), isglobal=True, intelgroup_id=groupid)
					else:
						Tags.objects.create(name=tag.strip(), isglobal=False, intelgroup_id=groupid)
			ftr = "http://ftr-premium.fivefilters.org/"
			encode = urllib.parse.quote_plus(data['url'])
			key = urllib.parse.quote_plus("KSF8GH22GZRKA8")
			req = urllib.request.Request(ftr+"makefulltextfeed.php?url="+encode+"&key="+key+"&max=25")
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
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv4', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'ipv4cidr' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv4 CIDR', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'ipv4range' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv4 range', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'ipv6addr' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'ipv6cidr' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6 CIDR', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'ipv6range' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6 CIDR', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'md5' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='Hash', type_api='hash', value='MD5', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'sha1' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='Hash', type_api='hash', value='SHA1', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'sha256' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='Hash', type_api='hash', value='SHA256', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'ssdeep' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='Hash', type_api='hash', value='Ssdeep', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'fqdn' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='System', type_api='system', value='FQDN', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'url' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='System', type_api='system', value='URL', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'useragent' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='System', type_api='system', value='User Agent', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'email' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='System', type_api='system', value='Email Address', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'filename' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='System', type_api='system', value='Filename', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'filepath' and len(results[result])>0:
								temp = []
								for re in results[result]:
									if '\t' in re or '\n' in re or r'\u20' in re:
										temp = list(results[result]).remove(re)
								if temp != None:
									if temp != []:
										temp.reverse()
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											GlobalIndicators.objects.create(type='System', type_api='system', value='filepath', value_api=result)
										Indicators.objects.create(value=','.join(temp), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'regkey' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='System', type_api='system', value='Registry Key', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'asn' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ASN', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'asnown' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ASN Owner', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'cc' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='Country', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'isp' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ISP', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'cve' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='CVE', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'malware' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Malware', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'attacktype' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Attack Type', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'incident' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Incident', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							elif result == 'topic' and len(results[result])>0:
								if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
									GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Topic', value_api=result)
								Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
							else:
								print('indicator->', result)
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
					elif(item == 'pubDate'):
						FeedItems.objects.filter(id=FeedItems.objects.last().id).update(pubdate=xmltodict.parse(contents)['rss']['channel']['item'][item])
					elif(item == 'source'):
						FeedItems.objects.filter(id=FeedItems.objects.last().id).update(source=xmltodict.parse(contents)['rss']['channel']['item'][item])
					else:
						print('item->', item)
			if type(xmltodict.parse(contents)['rss']['channel']['item']) is list:
				for items in xmltodict.parse(contents)['rss']['channel']['item']:
					FeedItems.objects.create(feed_id=Feeds.objects.last().id)
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
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv4', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'ipv4cidr' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv4 CIDR', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'ipv4range' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv4 range', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'ipv6addr' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'ipv6cidr' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6 CIDR', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'ipv6range' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6 CIDR', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'md5' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='Hash', type_api='hash', value='MD5', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'sha1' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='Hash', type_api='hash', value='SHA1', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'sha256' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='Hash', type_api='hash', value='SHA256', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'ssdeep' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='Hash', type_api='hash', value='Ssdeep', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'fqdn' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='System', type_api='system', value='FQDN', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'url' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='System', type_api='system', value='URL', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'useragent' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='System', type_api='system', value='User Agent', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'email' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='System', type_api='system', value='Email Address', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'filename' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='System', type_api='system', value='Filename', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'filepath' and len(results[result])>0:
									temp = []
									for re in results[result]:
										if '\t' in re or '\n' in re or r'\u20' in re:
											temp = list(results[result]).remove(re)
									if temp != None:
										if temp != []:
											temp.reverse()
											if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
												GlobalIndicators.objects.create(type='System', type_api='system', value='filepath', value_api=result)
											Indicators.objects.create(value=','.join(temp), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'regkey' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='System', type_api='system', value='Registry Key', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'asn' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ASN', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'asnown' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ASN Owner', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'cc' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='Country', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'isp' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ISP', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'cve' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='CVE', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'malware' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Malware', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'attacktype' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Attack Type', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'incident' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Incident', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'topic' and len(results[result])>0:
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Topic', value_api=result)
									Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								else:
									print('indicator->', result)
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
						elif(item == 'pubDate'):
							FeedItems.objects.filter(id=FeedItems.objects.last().id).update(pubdate=items[item])
						elif(item == 'source'):
							FeedItems.objects.filter(id=FeedItems.objects.last().id).update(source=items[item])
						else:
							print('item->', item)
		for item in FeedItems.objects.filter(feed_id=Feeds.objects.last().id).all():
			IntelReports.objects.create(groupfeed_id=GroupFeeds.objects.last().id, intelgroup_id=groupid, feeditem_id=item.id)
		flag = True
		is_exist = True
		for item in FeedItems.objects.filter(feed_id=Feeds.objects.last().id).all():
			while flag:
				if len(WebHooks.objects.filter(intelgroup_id=groupid).order_by('id').all()) > 0:
					for webhook in WebHooks.objects.filter(intelgroup_id=groupid).order_by('id').all():
						channelunique = FeedChannels.objects.filter(feed_id=Feeds.objects.last().id).last().uniqueid
						groupunique = IntelGroups.objects.filter(id=groupid).last().uniqueid
						data = {
							'uuid': webhook.uniqueid,
							'channel': channelunique,
							'intelgroup': groupunique,
							'reporturl': f"{settings.SITE_ROOT_URL}/home/report/"+str(IntelReports.objects.last().id),
							'addedtime': IntelReports.objects.last().created_at,
							'data': {
								'title': item.title,
								'link': item.link,
								'description': item.description
							}
						}
						try:
							requests.post(webhook.endpoint, data=data)
						except Exception as e:
							print(str(e))
							flag = False
				else:
					flag = False
					is_exist = False
		webhook_fail = False
		if is_exist and not flag :
			webhook_fail=True	
		groupfeeds = []
		groupfeedids = []
		for groupfeed in GroupFeeds.objects.filter(intelgroup_id=groupid).order_by('id').all():
			serializer = GroupCategoryFeedSerializer(groupfeed)
			if serializer.data['feed']['isglobal']:
				groupfeeds.append(serializer.data)
			groupfeedids.append(groupfeed.feed_id)
		feeds = FeedCategorySerializer(Feeds.objects.exclude(id__in=groupfeedids).filter(isglobal=True).order_by('id').all(), many=True)
		return Response({'groupfeeds':groupfeeds, 'feeds':feeds.data, 'webhook_fail':webhook_fail, 'isUrlExist':isUrlExist})
	if request.method == 'PUT':
		data = request.data
		feed = Feeds.objects.filter(id=data['id']).last()
		
		GroupFeeds.objects.create(feed_id=data['id'], intelgroup_id=data['groupid'], isenable=True)
		groupfeed = GroupFeeds.objects.last()
		if data['name'] == '':
			GroupFeeds.objects.filter(id=groupfeed.id).update(name=feed.name)
		else:
			GroupFeeds.objects.filter(id=groupfeed.id).update(name=data['name'])
		if data['description'] == '':
			GroupFeeds.objects.filter(id=groupfeed.id).update(description=feed.description)
		else:
			GroupFeeds.objects.filter(id=groupfeed.id).update(description=data['description'])
		if data['tags'] == '':
			GroupFeeds.objects.filter(id=groupfeed.id).update(tags=feed.tags)
		else:
			GroupFeeds.objects.filter(id=groupfeed.id).update(tags=data['tags'])
		if data['confidence'] == '':
			GroupFeeds.objects.filter(id=groupfeed.id).update(confidence=feed.confidence)
		else:
			GroupFeeds.objects.filter(id=groupfeed.id).update(confidence=data['confidence'])
		if data['category'] == '':
			GroupFeeds.objects.filter(id=groupfeed.id).update(category_id=feed.category_id)
		else:
			GroupFeeds.objects.filter(id=groupfeed.id).update(category_id=data['category'])
		for item in FeedItems.objects.filter(feed_id=Feeds.objects.last().id).all():
			IntelReports.objects.create(feeditem_id=item.id, groupfeed_id=GroupFeeds.objects.last().id, intelgroup_id=request.data['groupid'])
		flag = True
		is_exist = True
		for item in FeedItems.objects.filter(feed_id=Feeds.objects.last().id).all():
			while flag:
				if len(WebHooks.objects.filter(intelgroup_id=data['groupid']).order_by('id').all()) > 0:
					for webhook in WebHooks.objects.filter(intelgroup_id=data['groupid']).order_by('id').all():
						channelunique = FeedChannels.objects.filter(feed_id=data['id']).last().uniqueid
						groupunique = IntelGroups.objects.filter(id=data['groupid']).last().uniqueid
						data = {
							'uuid': webhook.uniqueid,
							'channel': channelunique,
							'intelgroup': groupunique,
							'reporturl': f"{settings.SITE_ROOT_URL}/home/report/"+str(IntelReports.objects.last().id),
							'addedtime': IntelReports.objects.last().created_at,
							'data': {
								'title': item.title,
								'link': item.link,
								'description': item.description
							}
						}
						try:
							requests.post(webhook.endpoint, data=data)
						except Exception as e:
							print(str(e))
							flag = False
				else:
					flag = False
					is_exist = False
		webhook_fail = False
		if is_exist and not flag:
			webhook_fail=True			
		groupfeeds = []
		groupfeedids = []
		for groupfeed in GroupFeeds.objects.filter(intelgroup_id=data['groupid']).order_by('id').all():
			serializer = GroupCategoryFeedSerializer(groupfeed)
			if serializer.data['feed']['isglobal']:
				groupfeeds.append(serializer.data)
			groupfeedids.append(groupfeed.feed_id)
		feeds = FeedCategorySerializer(Feeds.objects.exclude(id__in=groupfeedids).filter(isglobal=True).order_by('id').all(), many=True)
		return Response({'groupfeeds':groupfeeds, 'feeds':feeds.data, 'webhook_fail':webhook_fail})

@swagger_auto_schema(methods=['post'], request_body=IDSerializer, responses={201: FeedCategorySerializer})
@api_view(['POST'])
def feedlist(request):
	customfeeds = True
	groupfeeds = []
	groupfeedids = []
	if request.data['id'] != '':
		created_at = IntelGroups.objects.filter(id=request.data['id']).last().created_at
		subid = IntelGroups.objects.filter(id=request.data['id']).last().plan_id
		if subid != None:
			planid = Subscription.objects.filter(djstripe_id=subid).last().plan_id
			productid = Plan.objects.filter(djstripe_id=planid).last().product_id
			if Product.objects.filter(djstripe_id=productid).last().metadata['custom_feeds'] == 'false':
				customfeeds = False
		for groupfeed in GroupFeeds.objects.filter(intelgroup_id=request.data['id']).order_by('id').all():
			serializer = GroupCategoryFeedSerializer(groupfeed)
			if serializer.data['feed']['isglobal']:
				groupfeeds.append(serializer.data)
			groupfeedids.append(groupfeed.feed_id)
	feeds = FeedCategorySerializer(Feeds.objects.exclude(id__in=groupfeedids).filter(isglobal=True).order_by('id').all(), many=True)
	categories = CategorySerializer(Categories.objects.order_by('id').all(), many=True)
	tags = TagSerializer(Tags.objects.order_by('id').all(), many=True)
	return Response({'feedlist':feeds.data, 'groupfeeds':groupfeeds, 'categories':categories.data, 'tags':tags.data, 'customfeeds':customfeeds})

@swagger_auto_schema(methods=['post'], request_body=IDSerializer, responses={201: GroupCategoryFeedSerializer})
@swagger_auto_schema(methods=['put'], request_body=FeedUpdateSerializer, responses={200: GroupCategoryFeedSerializer})
@swagger_auto_schema(methods=['delete'], request_body=IDSerializer, responses={204: GroupCategoryFeedSerializer})
@swagger_auto_schema(methods=['patch'], request_body=FeedUpdateSerializer, responses={203: GroupCategoryFeedSerializer})
@api_view(['POST', 'PUT', 'DELETE', 'PATCH'])
def configuredfeeds(request):
	if request.method == 'POST':
		configuredfeeds = GroupCategoryFeedSerializer(GroupFeeds.objects.filter(intelgroup_id=request.data['id']).order_by('id').all(), many=True)
		feedids = []
		feeditemids = []
		for groupfeed in GroupFeeds.objects.filter(intelgroup_id=request.data['id']).order_by('id').all():
			feedids.append(groupfeed.feed_id)
		channels = FeedChannelSerializer(FeedChannels.objects.filter(feed_id__in=feedids).order_by('id').all(), many=True)
		collections = []
		for feedid in feedids:
			indicators = []
			for item in FeedItems.objects.filter(feed_id=feedid).order_by('id').all():
				for indicator in Indicators.objects.filter(feeditem_id=item.id).order_by('id').all():
					indicators.append(indicator)
			globalids = []
			for indicator in indicators:
				flag = True
				for globalid in globalids:
					if globalid == indicator.globalindicator_id:
						flag = False
				if flag:
					globalids.append(indicator.globalindicator_id)
			collections.append({'feedid':feedid, 'count':len(globalids)})
		categories = CategorySerializer(Categories.objects.order_by('id').all(), many=True)
		tags = TagSerializer(Tags.objects.order_by('id').all(), many=True)
		return Response({'configuredfeeds':configuredfeeds.data, 'categories':categories.data, 'tags':tags.data, 'channels':channels.data, 'collections':collections})
	elif request.method == 'PUT':
		if 'name' in request.data:
			if request.data['name'] != '':
				GroupFeeds.objects.filter(id=request.data['id']).update(name=request.data['name'])
			if request.data['description'] != '':
				GroupFeeds.objects.filter(id=request.data['id']).update(description=request.data['description'])
			if request.data['category'] != '':
				GroupFeeds.objects.filter(id=request.data['id']).update(category_id=request.data['category'])
			if request.data['tags'] != '':
				GroupFeeds.objects.filter(id=request.data['id']).update(tags=request.data['tags'])
			if request.data['confidence'] != '':
				GroupFeeds.objects.filter(id=request.data['id']).update(confidence=request.data['confidence'])
			if not GroupFeeds.objects.filter(id=request.data['id']).last().isenable:
				GroupFeeds.objects.filter(id=request.data['id']).update(isenable=True)
			configuredfeeds = GroupCategoryFeedSerializer(GroupFeeds.objects.filter(intelgroup_id=GroupFeeds.objects.filter(id=request.data['id']).last().intelgroup_id).order_by('id').all(), many=True)
			return Response(configuredfeeds.data)
		else:
			if GroupFeeds.objects.filter(id=request.data['id']).last().isenable:
				GroupFeeds.objects.filter(id=request.data['id']).update(isenable=False)
			else:
				GroupFeeds.objects.filter(id=request.data['id']).update(isenable=True)
			configuredfeeds = GroupCategoryFeedSerializer(GroupFeeds.objects.filter(intelgroup_id=GroupFeeds.objects.filter(id=request.data['id']).last().intelgroup_id).order_by('id').all(), many=True)
			return Response(configuredfeeds.data)
	elif request.method == 'DELETE':
		groupid = GroupFeeds.objects.filter(id=request.data['id']).last().intelgroup_id
		GroupFeeds.objects.filter(id=request.data['id']).delete()
		configuredfeeds = GroupCategoryFeedSerializer(GroupFeeds.objects.filter(intelgroup_id=groupid).order_by('id').all(), many=True)
		return Response(configuredfeeds.data)
	elif request.method == 'PATCH':
		currentgroup = int(request.data['currentgroup'])
		role = UserIntelGroupRoles.objects.filter(user_id=request.user.id, intelgroup_id=currentgroup).last().role
		if role == 2:
			if(request.data['category'] == '' and request.data['tags'] == '' and request.data['confidence'] == ''):
				configuredfeeds = GroupCategoryFeedSerializer(GroupFeeds.objects.filter(intelgroup_id=currentgroup).order_by('id').all(), many=True)
			if(request.data['category'] != '' and request.data['tags'] == '' and request.data['confidence'] == ''):
				configuredfeeds = GroupCategoryFeedSerializer(GroupFeeds.objects.filter(intelgroup_id=currentgroup, category_id=request.data['category']).order_by('id').all(), many=True)
			if(request.data['category'] == '' and request.data['tags'] != '' and request.data['confidence'] == ''):
				configuredfeeds = GroupCategoryFeedSerializer(GroupFeeds.objects.filter(intelgroup_id=currentgroup, tags__contains=request.data['tags']).order_by('id').all(), many=True)
			if(request.data['confidence'] != '' and request.data['tags'] == '' and request.data['category'] == ''):
				configuredfeeds = GroupCategoryFeedSerializer(GroupFeeds.objects.filter(intelgroup_id=currentgroup, confidence__gte=request.data['confidence']).order_by('id').all(), many=True)
			if(request.data['confidence'] != '' and request.data['category'] != '' and request.data['tags'] == ''):
				configuredfeeds = GroupCategoryFeedSerializer(GroupFeeds.objects.filter(intelgroup_id=currentgroup, confidence__gte=request.data['confidence'], category_id=request.data['category']).order_by('id').all(), many=True)
			if(request.data['confidence'] != '' and request.data['tags'] != '' and request.data['category'] == ''):
				configuredfeeds = GroupCategoryFeedSerializer(GroupFeeds.objects.filter(intelgroup_id=currentgroup, confidence__gte=request.data['confidence'], tags__contains=request.data['tags']).order_by('id').all(), many=True)
			if(request.data['category'] != '' and request.data['tags'] != '' and request.data['confidence'] == ''):
				configuredfeeds = GroupCategoryFeedSerializer(GroupFeeds.objects.filter(intelgroup_id=currentgroup, tags__contains=request.data['tags'], category_id = request.data['category']).order_by('id').all(), many=True)
			if(request.data['category'] != '' and request.data['tags'] != '' and request.data['confidence'] != ''):
				configuredfeeds = GroupCategoryFeedSerializer(GroupFeeds.objects.filter(intelgroup_id=currentgroup, tags__contains=request.data['tags'], category_id = request.data['category'], confidence__gte=request.data['confidence']).order_by('id').all(), many=True)
			return Response(configuredfeeds.data)
		elif role == 1:
			if(request.data['category'] == '' and request.data['tags'] == '' and request.data['confidence'] == ''):
				configuredfeeds = GroupCategoryFeedSerializer(GroupFeeds.objects.filter(isenable=True, intelgroup_id=currentgroup).order_by('id').all(), many=True)
			if(request.data['category'] != '' and request.data['tags'] == '' and request.data['confidence'] == ''):
				configuredfeeds = GroupCategoryFeedSerializer(GroupFeeds.objects.filter(isenable=True, intelgroup_id=currentgroup, category_id=request.data['category']).order_by('id').all(), many=True)
			if(request.data['category'] == '' and request.data['tags'] != '' and request.data['confidence'] == ''):
				configuredfeeds = GroupCategoryFeedSerializer(GroupFeeds.objects.filter(isenable=True, intelgroup_id=currentgroup, tags__contains=request.data['tags']).order_by('id').all(), many=True)
			if(request.data['confidence'] != '' and request.data['tags'] == '' and request.data['category'] == ''):
				configuredfeeds = GroupCategoryFeedSerializer(GroupFeeds.objects.filter(isenable=True, intelgroup_id=currentgroup, confidence__gte=request.data['confidence']).order_by('id').all(), many=True)
			if(request.data['confidence'] != '' and request.data['category'] != '' and request.data['tags'] == ''):
				configuredfeeds = GroupCategoryFeedSerializer(GroupFeeds.objects.filter(isenable=True, intelgroup_id=currentgroup, confidence__gte=request.data['confidence'], category_id=request.data['category']).order_by('id').all(), many=True)
			if(request.data['confidence'] != '' and request.data['tags'] != '' and request.data['category'] == ''):
				configuredfeeds = GroupCategoryFeedSerializer(GroupFeeds.objects.filter(isenable=True, intelgroup_id=currentgroup, confidence__gte=request.data['confidence'], tags__contains=request.data['tags']).order_by('id').all(), many=True)
			if(request.data['category'] != '' and request.data['tags'] != '' and request.data['confidence'] == ''):
				configuredfeeds = GroupCategoryFeedSerializer(GroupFeeds.objects.filter(isenable=True, intelgroup_id=currentgroup, tags__contains=request.data['tags'], category_id = request.data['category']).order_by('id').all(), many=True)
			if(request.data['category'] != '' and request.data['tags'] != '' and request.data['confidence'] != ''):
				configuredfeeds = GroupCategoryFeedSerializer(GroupFeeds.objects.filter(isenable=True, intelgroup_id=currentgroup, tags__contains=request.data['tags'], category_id = request.data['category'], confidence__gte=request.data['confidence']).order_by('id').all(), many=True)
			return Response(configuredfeeds.data)

@swagger_auto_schema(methods=['post'], request_body=SearchFeedSerializer, responses={201: FeedCategorySerializer})
@api_view(['POST'])
def searchfeeds(request):
	currentgroup = int(request.data['currentgroup'])
	if(request.data['category'] == '' and request.data['tags'] == '' and request.data['confidence'] == ''):
		groupfeeds = []
		groupfeedids = []
		for groupfeed in GroupFeeds.objects.filter(intelgroup_id=currentgroup).order_by('id').all():
			serializer = GroupCategoryFeedSerializer(groupfeed)
			if serializer.data['feed']['isglobal']:
				groupfeeds.append(serializer.data)
			groupfeedids.append(groupfeed.feed_id)
		feeds = FeedCategorySerializer(Feeds.objects.exclude(id__in=groupfeedids).filter(isglobal=True).order_by('id').all(), many=True)
	if(request.data['category'] != '' and request.data['tags'] == '' and request.data['confidence'] == ''):
		groupfeeds = []
		groupfeedids = []
		for groupfeed in GroupFeeds.objects.filter(intelgroup_id=currentgroup, category_id = request.data['category']).order_by('id').all():
			serializer = GroupCategoryFeedSerializer(groupfeed)
			if serializer.data['feed']['isglobal']:
				groupfeeds.append(serializer.data)
			groupfeedids.append(groupfeed.feed_id)
		feeds = FeedCategorySerializer(Feeds.objects.exclude(id__in=groupfeedids).filter(isglobal=True, category_id = request.data['category']).order_by('id').all(), many=True)
	if(request.data['category'] == '' and request.data['tags'] != '' and request.data['confidence'] == ''):
		groupfeeds = []
		groupfeedids = []
		for groupfeed in GroupFeeds.objects.filter(intelgroup_id=currentgroup, tags__contains=request.data['tags']).order_by('id').all():
			serializer = GroupCategoryFeedSerializer(groupfeed)
			if serializer.data['feed']['isglobal']:
				groupfeeds.append(serializer.data)
			groupfeedids.append(groupfeed.feed_id)
		feeds = FeedCategorySerializer(Feeds.objects.exclude(id__in=groupfeedids).filter(isglobal=True, tags__contains=request.data['tags']).order_by('id').all(), many=True)
	if(request.data['confidence'] != '' and request.data['tags'] == '' and request.data['category'] == ''):
		groupfeeds = []
		groupfeedids = []
		for groupfeed in GroupFeeds.objects.filter(intelgroup_id=currentgroup, confidence__gte=request.data['confidence']).order_by('id').all():
			serializer = GroupCategoryFeedSerializer(groupfeed)
			if serializer.data['feed']['isglobal']:
				groupfeeds.append(serializer.data)
			groupfeedids.append(groupfeed.feed_id)
		feeds = FeedCategorySerializer(Feeds.objects.exclude(id__in=groupfeedids).filter(isglobal=True, confidence__gte=request.data['confidence']).order_by('id').all(), many=True)
	if(request.data['confidence'] != '' and request.data['category'] != '' and request.data['tags'] == ''):
		groupfeeds = []
		groupfeedids = []
		for groupfeed in GroupFeeds.objects.filter(intelgroup_id=currentgroup, confidence__gte=request.data['confidence'], category_id=request.data['category']).order_by('id').all():
			serializer = GroupCategoryFeedSerializer(groupfeed)
			if serializer.data['feed']['isglobal']:
				groupfeeds.append(serializer.data)
			groupfeedids.append(groupfeed.feed_id)
		feeds = FeedCategorySerializer(Feeds.objects.exclude(id__in=groupfeedids).filter(isglobal=True, confidence__gte=request.data['confidence'], category_id=request.data['category']).order_by('id').all(), many=True)
	if(request.data['confidence'] != '' and request.data['tags'] != '' and request.data['category'] == ''):
		groupfeeds = []
		groupfeedids = []
		for groupfeed in GroupFeeds.objects.filter(intelgroup_id=currentgroup, confidence__gte=request.data['confidence'], tags__contains=request.data['tags']).order_by('id').all():
			serializer = GroupCategoryFeedSerializer(groupfeed)
			if serializer.data['feed']['isglobal']:
				groupfeeds.append(serializer.data)
			groupfeedids.append(groupfeed.feed_id)
		feeds = FeedCategorySerializer(Feeds.objects.exclude(id__in=groupfeedids).filter(isglobal=True, confidence__gte=request.data['confidence'], tags__contains=request.data['tags']).order_by('id').all(), many=True)
	if(request.data['category'] != '' and request.data['tags'] != '' and request.data['confidence'] == ''):
		groupfeeds = []
		groupfeedids = []
		for groupfeed in GroupFeeds.objects.filter(intelgroup_id=currentgroup, tags__contains=request.data['tags'], category_id = request.data['category']).order_by('id').all():
			serializer = GroupCategoryFeedSerializer(groupfeed)
			if serializer.data['feed']['isglobal']:
				groupfeeds.append(serializer.data)
			groupfeedids.append(groupfeed.feed_id)
		feeds = FeedCategorySerializer(Feeds.objects.exclude(id__in=groupfeedids).filter(isglobal=True, tags__contains=request.data['tags'], category_id = request.data['category']).order_by('id').all(), many=True)
	if(request.data['category'] != '' and request.data['tags'] != '' and request.data['confidence'] != ''):
		groupfeeds = []
		groupfeedids = []
		for groupfeed in GroupFeeds.objects.filter(intelgroup_id=currentgroup, tags__contains=request.data['tags'], category_id = request.data['category'], confidence__gte=request.data['confidence']).order_by('id').all():
			serializer = GroupCategoryFeedSerializer(groupfeed)
			if serializer.data['feed']['isglobal']:
				groupfeeds.append(serializer.data)
			groupfeedids.append(groupfeed.feed_id)
		feeds = FeedCategorySerializer(Feeds.objects.exclude(id__in=groupfeedids).filter(isglobal=True, tags__contains=request.data['tags'], category_id = request.data['category'], confidence__gte=request.data['confidence']).order_by('id').all(), many=True)
	return Response({'feeds':feeds.data, 'groupfeeds':groupfeeds})

@swagger_auto_schema(methods=['put'], request_body=GroupIDSerializer, responses={200: FeedCategorySerializer})
@api_view(['PUT'])
def feedenable(request):
	if request.data['groupid'] == '':
		groupid = UserIntelGroupRoles.objects.filter(user_id=request.user.id).order_by('intelgroup_id').last().intelgroup_id
	else:
		groupid = request.data['groupid']
	feed = Feeds.objects.filter(id=request.data['id']).last()
	GroupFeeds.objects.create(feed_id=request.data['id'], intelgroup_id=groupid, name=feed.name, description=feed.description, tags=feed.tags, confidence=feed.confidence, category_id=feed.category_id, isenable=True )
	for item in FeedItems.objects.filter(feed_id=request.data['id']).all():
		IntelReports.objects.create(feeditem_id=item.id, groupfeed_id=GroupFeeds.objects.last().id, intelgroup_id=groupid)
	flag = True
	is_exist = True
	for item in FeedItems.objects.filter(feed_id=request.data['id']).all():
		while flag:
			if len(WebHooks.objects.filter(intelgroup_id=groupid, isenable=True).order_by('id').all()) > 0:
				for webhook in WebHooks.objects.filter(intelgroup_id=groupid, isenable=True).order_by('id').all():
					channelunique = FeedChannels.objects.filter(feed_id=request.data['id']).last().uniqueid
					groupunique = IntelGroups.objects.filter(id=groupid).last().uniqueid
					data = {
						'uuid': webhook.uniqueid,
						'channel': channelunique,
						'intelgroup': groupunique,
						'reporturl': f"{settings.SITE_ROOT_URL}/home/report/"+str(IntelReports.objects.filter(feeditem_id=item.id).last().id),
						'addedtime': IntelReports.objects.filter(feeditem_id=item.id).last().created_at,
						'data': {
							'title': item.title,
							'link': item.link,
							'description': item.description
						}
					}
					try:
						requests.post(webhook.endpoint, data=data)
					except Exception as e:
						print(str(e))
						flag = False
			else:
				flag = False
				is_exist = False
	webhook_fail = False
	if is_exist and not flag:
		webhook_fail = True
	groupfeeds = []
	groupfeedids = []
	for groupfeed in GroupFeeds.objects.filter(intelgroup_id=groupid).order_by('id').all():
		serializer = GroupCategoryFeedSerializer(groupfeed)
		if serializer.data['feed']['isglobal']:
			groupfeeds.append(serializer.data)
		groupfeedids.append(groupfeed.feed_id)
	feeds = FeedCategorySerializer(Feeds.objects.exclude(id__in=groupfeedids).filter(isglobal=True).order_by('id').all(), many=True)
	return Response({'groupfeeds':groupfeeds, 'feeds':feeds.data, 'webhook_fail':webhook_fail})

@swagger_auto_schema(methods=['post'], request_body=AttributeCreateSerializer, responses={201: UserGroupAttributeSerializer})
@swagger_auto_schema(methods=['put'], request_body=AttributeUpdateSerializer, responses={200: UserGroupAttributeSerializer})
@api_view(['POST', 'PUT'])
def attributes(request):
	if request.method == 'POST':
		if 'attribute' in request.data:
			for attribute in Attributes.objects.filter(intelgroup_id=request.data['currentgroup']):
				if attribute.attribute == request.data['attribute'] and attribute.value == request.data['value']:
					return Response({'message':True})
			Attributes.objects.create(attribute=request.data['attribute'],api_attribute='_'.join(request.data['attribute'].split(' ')).lower(), value=request.data['value'], api_value='_'.join(request.data['value'].split(' ')).lower(), words_matched=request.data['words_matched'], isenable=request.data['isenable'], user_id=request.user.id, intelgroup_id=request.data['currentgroup'])
			create_data = Attributes.objects.filter(user_id=request.user.id).last()
			serializer = UserGroupAttributeSerializer(create_data)
			return Response(serializer.data)
		else:
			if request.data['currentgroup'] == '':
				groupid = IntelGroups.objects.order_by('id').first().id
			else:
				groupid = request.data['currentgroup']
			created_at = IntelGroups.objects.filter(id=groupid).last().created_at
			subid = IntelGroups.objects.filter(id=groupid).last().plan_id
			customobservable = True
			if subid != None:
				planid = Subscription.objects.filter(djstripe_id=subid).last().plan_id
				productid = Plan.objects.filter(djstripe_id=planid).last().product_id
				if Product.objects.filter(djstripe_id=productid).last().metadata['custom_observables'] == 'false':
					customobservable = False
			attributes = Attributes.objects.filter(intelgroup_id=groupid).order_by('id').all()
			attribute_serializer = UserGroupAttributeSerializer(attributes, many=True)
			enableglobalattributes = GroupGlobalAttributeSerializer(GroupGlobalAttributes.objects.filter(intelgroup_id=groupid).all(), many=True)
			return Response({'attributes':attribute_serializer.data, 'globalattributes':enableglobalattributes.data, 'customobservable':customobservable})
	elif request.method == 'PUT':
		Attributes.objects.filter(id=request.data['id']).update(attribute=request.data['attribute'],api_attribute='_'.join(request.data['attribute'].split(' ')).lower(), value=request.data['value'], api_value='_'.join(request.data['value'].split(' ')).lower(), words_matched=request.data['words_matched'], isenable=request.data['isenable'], user_id=request.user.id, intelgroup_id=request.data['currentgroup'])
		serializer = UserGroupAttributeSerializer(Attributes.objects.filter(id=request.data['id']).all()[0])
		return Response(serializer.data)

@swagger_auto_schema(methods=['post'], request_body=EnabledSerializer, responses={201: UserGroupAttributeSerializer})
@api_view(['POST'])
def enableglobal(request):
	GroupGlobalAttributes.objects.filter(id=request.data['id']).update(isenable=request.data['isenable'])
	serializer = GroupGlobalAttributeSerializer(GroupGlobalAttributes.objects.filter(id=request.data['id']).last())
	return Response(serializer.data)

@swagger_auto_schema(methods=['post'], request_body=WhitelistCreateSerializer, responses={201: UserGroupAttributeSerializer})
@swagger_auto_schema(methods=['put'], request_body=EnabledSerializer, responses={200: UserGroupAttributeSerializer})
@api_view(['POST', 'PUT'])
def whitelist(request):
	if request.method == 'POST':
		if not 'indicator' in request.data:
			feedids = []
			feeditemids = []
			if request.data['currentgroup'] == '':
				groupid = IntelGroups.objects.order_by('id').first().id
			else:
				groupid = request.data['currentgroup']
			for feed in GroupFeeds.objects.filter(intelgroup_id=groupid).all():
				feedids.append(feed.feed_id)
			for feeditem in FeedItems.objects.filter(feed_id__in=feedids).all():
				feeditemids.append(feeditem.id)
			indicator_serializer = IndicatorGlobalSerializer(Indicators.objects.filter(feeditem_id__in=feeditemids).order_by('id').all(), many=True)
			whitelist_serializer = UserIndicatorWhitelistSerializer(Whitelists.objects.order_by('id').all(), many=True)
			global_serializer = GlobalIndicatorSerializer(GlobalIndicators.objects.order_by('id').all(), many=True)
			return Response({'indicators': indicator_serializer.data, 'whitelist': whitelist_serializer.data, 'globalindicators': global_serializer.data})
		else:
			flag = True
			if len(Whitelists.objects.filter(globalindicator_id=request.data['indicator'],value=request.data['value']).all())>0:
				return Response({'message': True})
			else:
				Whitelists.objects.create(globalindicator_id=request.data['indicator'],value=request.data['value'], user_id=request.user.id, enabled=request.data['enabled'] )
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
	if Indicators.objects.filter(id=request.data['id']).last().isenable:
		Indicators.objects.filter(id=request.data['id']).update(isenable=False)
	else:
		Indicators.objects.filter(id=request.data['id']).update(isenable=True)
	serializer = GlobalItemIndicatorSerializer(Indicators.objects.filter(id=request.data['id']).all()[0])
	return Response(serializer.data)

@swagger_auto_schema(methods=['post'], request_body=InviteSerializer, responses={201: UserIntelGroupRolesSerializer})
@api_view(['POST'])
def invite(request):
	userids = []
	for email in request.data['emails']:
		if len(CustomUser.objects.filter(email=email).all()) != 0:
			userids.append(CustomUser.objects.filter(email=email).last().id)
	created_at = IntelGroups.objects.filter(id=request.data['group_id']).last().created_at
	subid = IntelGroups.objects.filter(id=request.data['group_id']).last().plan_id
	flag = False
	if subid == None:
		if datetime.now()<created_at.replace(tzinfo=None)+timedelta(days=1):
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
		try:
			send_mail(
				f'You’ve been invited to join the {groupname} Intel Group on Cyobstract',
				f'''From: {settings.FROM}
Name: Sherlock at Cyobstract
Reply-to: {settings.REPLY}.com
Title: You've been invited to join the {groupname} Intel Group on Cyobstract
Hello!
{settings.SMTP_USER} has invited to join the {groupname} Intel Group on Cyobstract as a Member.
By accepting this invitation, you’ll have access to all intelligence curated by the other members of the {groupname} Intel Group.
To confirm or reject this invitation, click the link below.
{settings.SITE_ROOT_URL}
If you have any questions, simply reply to this email to get in contact with a real person on the team.
Sherlock and the Cyobstract Team''',
				settings.SMTP_USER,
				request.data['emails'],
				fail_silently=False
			)
		except:
			print('email sending error!')
		users = [];
		for userid in userids:
			existing_user = UserIntelGroupRoles.objects.filter(intelgroup_id=request.data['group_id'], user_id=userid).all()
			if len(existing_user) == 0:
				UserIntelGroupRoles.objects.create(intelgroup_id=request.data['group_id'], user_id=userid, role=0)
				user = UserIntelGroupRoles.objects.filter(intelgroup_id=request.data['group_id'], user_id=userid, role=0).all()
				serializer = UserIntelGroupRolesSerializer(user[0])
				users.append(serializer.data)
		if(len(users) == 0):
				users={'role': True}
		return Response(users)
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

@swagger_auto_schema(methods=['get'], responses={200: RoleGroupSerializer})
@api_view(['GET'])
def home(request):
	groups = RoleGroupSerializer(UserIntelGroupRoles.objects.order_by('intelgroup_id').exclude(role=4).filter(user_id=request.user.id).all(), many=True).data
	# if len(groups) > 0:
	# 	CustomUser.objects.filter(id=request.user.id).update(onboarding=False)
	onboarding = CustomUser.objects.filter(id=request.user.id).last().onboarding
	return Response({'mygroups':groups, 'onboarding':onboarding})

@swagger_auto_schema(methods=['delete'], request_body=IDSerializer, responses={200: RoleGroupSerializer})
@api_view(['DELETE'])
def leavegroup(request):
	result = []
	role = UserIntelGroupRoles.objects.filter(id=request.data['id']).last().role
	if role == 1:
		UserIntelGroupRoles.objects.filter(id=request.data['id']).delete()
		groups = RoleGroupSerializer(UserIntelGroupRoles.objects.filter(user_id=request.user.id).order_by('intelgroup_id').all(), many=True).data
	elif role == 2:
		intelgroup_id = UserIntelGroupRoles.objects.filter(id=request.data['id']).all()[0].intelgroup_id
		admins = UserIntelGroupRoles.objects.filter(intelgroup_id=intelgroup_id, role=2).all()
		users = UserIntelGroupRoles.objects.filter(intelgroup_id=intelgroup_id).all()
		if len(admins)==1:
			if len(users)==1:
				UserIntelGroupRoles.objects.filter(id=request.data['id']).delete()
				IntelGroups.objects.filter(id=intelgroup_id).delete()
				groups = RoleGroupSerializer(UserIntelGroupRoles.objects.filter(user_id=request.user.id).order_by('intelgroup_id').all(), many=True).data
			else:
				return Response({'message':True})
		else:
			UserIntelGroupRoles.objects.filter(id=request.data['id']).delete()
			groups = RoleGroupSerializer(UserIntelGroupRoles.objects.filter(user_id=request.user.id).order_by('intelgroup_id').all(), many=True).data
	elif role == 4:
		UserIntelGroupRoles.objects.filter(id=request.data['id']).delete()
		groups = RoleGroupSerializer(UserIntelGroupRoles.objects.filter(user_id=request.user.id).order_by('intelgroup_id').all(), many=True).data
	return Response(groups)

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
			userids = []
			for email in request.data['emails']:
				if len(CustomUser.objects.filter(email=email).all()) != 0:
					userids.append(CustomUser.objects.filter(email=email).last().id)
			name = ''
			if(request.data['name'] == ''):
				letters = string.digits
				name = 'Intel Group' + ''. join(random.choice(letters) for i in range(10))
			else:
				name = request.data['name']
			try:
				send_mail(
					f'You’ve been invited to join the {name} Intel Group on Cyobstract',
					f'''From: {settings.FROM}
Name: Sherlock at Cyobstract
Reply-to: {settings.REPLY}
Title: You've been invited to join the {name} Intel Group on Cyobstract
Hello!
{settings.SMTP_USER} has invited to join the {name} Intel Group on Cyobstract as a Member.
By accepting this invitation, you’ll have access to all intelligence curated by the other members of the {name} Intel Group.
To confirm or reject this invitation, click the link below.
{settings.SITE_ROOT_URL}
If you have any questions, simply reply to this email to get in contact with a real person on the team.
Sherlock and the Cyobstract Team''',
					settings.SMTP_USER,
					request.data['emails'],
					fail_silently=False
				)
			except Exception as e:
				print(str(e))
			IntelGroups.objects.create(name=name, description=request.data['description'])
			new_group = IntelGroups.objects.last()
			for globalattribute in GlobalAttributes.objects.all():
				GroupGlobalAttributes.objects.create(intelgroup_id=new_group.id, globalattribute_id=globalattribute.id, isenable=True)
			UserIntelGroupRoles.objects.create(intelgroup_id=new_group.id, user_id=request.user.id, role=2)
			for invite_id in userids:
				if invite_id != request.user.id:
					UserIntelGroupRoles.objects.create(intelgroup_id=new_group.id, user_id=invite_id, role=0)
			new_role = UserIntelGroupRoles.objects.filter(intelgroup_id=new_group.id, user_id=request.user.id).all()
			serializer = RoleGroupSerializer(new_role[0])
			return Response(serializer.data)
		else:
			name = IntelGroups.objects.filter(id=request.data['id']).last().name
			description = IntelGroups.objects.filter(id=request.data['id']).last().description
			ispublic = IntelGroups.objects.filter(id=request.data['id']).last().ispublic
			role = UserGroupRoleSerializer(UserIntelGroupRoles.objects.filter(user_id=request.user.id, intelgroup_id=request.data['id']).all()[0])
			return Response({'name':name, 'description':description, 'ispublic':ispublic, 'currentrole':role.data})
	if request.method == 'PUT':
		IntelGroups.objects.filter(id=request.data['id']).update(name=request.data['name'],description=request.data['description'], ispublic=request.data['ispublic'])
		new_role = UserIntelGroupRoles.objects.filter(intelgroup_id=request.data['id'], user_id=request.user.id).all()
		serializer = RoleGroupSerializer(new_role[0])
		return Response(serializer.data)

@api_view(['GET', 'POST'])
def grouplist(request):
	if request.method == 'GET':
		mygroupids = []
		for role in UserIntelGroupRoles.objects.filter(user_id=request.user.id).order_by('id').all():
			mygroupids.append(role.intelgroup_id)
		groups = IntelGroupSerializer(IntelGroups.objects.exclude(id__in=mygroupids).filter(ispublic=True).order_by('id').all(), many=True)
		return Response(groups.data)
	elif request.method == 'POST':
		UserIntelGroupRoles.objects.create(user_id=request.user.id, intelgroup_id=request.data['id'], role=4)
		roles = UserIntelGroupRoles.objects.filter(intelgroup_id=request.data['id'], role=2).order_by('id').all()
		for role in roles:
			try:
				send_mail(
					f'{request.user.email} has been sent you request to join your Intel Group',
					f'''From: {request.user.email}
Reply-to: {request.user.email}
Title: Invite Request
Hello!
{request.user.email} has been sent you request to join your Intel Group''',
					settings.SMTP_USER,
					CustomUser.objects.filter(id=role.user_id).last().email,
					fail_silently=False
				)
			except Exception as e:
				print(str(e))
		mygroupids = []
		for role in UserIntelGroupRoles.objects.filter(user_id=request.user.id).order_by('id').all():
			mygroupids.append(role.intelgroup_id)
		groups = IntelGroupSerializer(IntelGroups.objects.exclude(id__in=mygroupids).filter(ispublic=True).order_by('id').all(), many=True)
		return Response(groups.data)

@swagger_auto_schema(methods=['post'], request_body=AccepInviteSerializer, responses={201: RoleGroupSerializer})
@api_view(['POST'])
def acceptinvite(request):
	UserIntelGroupRoles.objects.filter(id=request.data['id']).update(role = '1')
	userid = UserIntelGroupRoles.objects.filter(id=request.data['id']).last().user_id
	useremail = CustomUser.objects.filter(id=userid).last().email
	groupid = UserIntelGroupRoles.objects.filter(id=request.data['id']).last().intelgroup_id
	groupname = IntelGroups.objects.filter(id=groupid).last().name
	try:
		send_mail(
			f'You’ve been invited to join the {groupname} Intel Group on Cyobstract',
			f'''From: {settings.FROM}
Name: Sherlock at Cyobstract
Reply-to: {settings.REPLY}
Title: {useremail} has accepted your invitation to join {groupname}
Hello!
This email is just to confirm {useremail} has accepted your invitation to join {groupname}
To manage members in your intel group, click the link below.
{settings.SITE_ROOT_URL}
Sherlock and the Cyobstract Team''',
			settings.SMTP_USER,
			request.user.email,
			fail_silently=False
		)
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
	try:
		send_mail(
			f'You’ve been invited to join the {groupname} Intel Group on Cyobstract',
			f'''From: {settings.FROM}
Name: Sherlock at Cyobstract
Reply-to: {settings.REPLY}
Title: {useremail} has rejected your invitation to join {groupname}
Hello!
{useremail} has rejected your invitation to join {groupname}
If you think this is a mistake, you can resend the invitation to {useremail} to join {groupname}.
To manage members in your intel group, click the link below:
{settings.SITE_ROOT_URL}
Sherlock and the Cyobstract Team''',
			settings.SMTP_USER,
			request.user.email,
			fail_silently=False
		)
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
		user_role = UserGroupRoleSerializer(UserIntelGroupRoles.objects.filter(intelgroup_id=request.data['groupid'], user_id=request.user.id).last())
		serializer = UserIntelGroupRolesSerializer(UserIntelGroupRoles.objects.filter(intelgroup_id=request.data['groupid']).all(), many=True)
		return Response({'myId':request.user.id, 'users':serializer.data, 'grouprole':user_role.data})
	if request.method == 'DELETE':
		
		if UserIntelGroupRoles.objects.filter(id=request.data['id']).last().role == 4:
			userid = UserIntelGroupRoles.objects.filter(id=request.data['id']).last().user_id
			groupid = UserIntelGroupRoles.objects.filter(id=request.data['id']).last().intelgroup_id
			groupname = IntelGroups.objects.filter(id=groupid).last().name
			try:
				send_mail(
					f'Your request has been refused from {groupname} Intel Group',
					f'''From: {request.user.email}
Reply-to: {request.user.email}
Title: Invite Refusing
Hello!
Your request has been refused from {groupname} Intel Group
If you think this is a mistake, you can resend the request to {groupname} Intel Group.
Sherlock and the Cyobstract Team''',
					settings.SMTP_USER,
					CustomUser.objects.filter(id=userid).last().email,
					fail_silently=False
				)
			except Exception as e:
				print(str(e))
		UserIntelGroupRoles.objects.filter(id=request.data['id']).delete()
		return Response('Success')

@swagger_auto_schema(methods=['post'], request_body=IDSerializer, responses={201: UserGroupRoleSerializer})
@api_view(['POST'])
def users(request):
	if request.method == 'POST':
		allusers = CustomUserSerializer(CustomUser.objects.exclude(is_staff=True).order_by('id').all(), many=True)
		user_role = UserGroupRoleSerializer(UserIntelGroupRoles.objects.all().filter(intelgroup_id=request.data['id'], user_id=request.user.id).last())
		users = UserGroupRoleSerializer(UserIntelGroupRoles.objects.filter(intelgroup_id=request.data['id']).all(), many=True)
		return Response({'myId':request.user.id, 'users':users.data, 'allusers':allusers.data, 'grouprole':user_role.data})
	
@swagger_auto_schema(methods=['post'], request_body=IDSerializer, responses={201: UserIntelGroupRolesSerializer})
@api_view(['POST'])
def changegroup(request, subscription_holder=None):
    
	isPlan = True
	isInit = False
	isAutoDown = False
	message = ''
	planname = ''
	subid = IntelGroups.objects.filter(id=request.data['id']).last().plan_id
	created_at = IntelGroups.objects.filter(id=request.data['id']).last().created_at
	currentrole = UserGroupRoleSerializer(UserIntelGroupRoles.objects.filter(user_id=request.user.id, intelgroup_id=request.data['id']).last())
	if not CustomUser.objects.filter(id=request.user.id).last().is_staff:
		if subid == None:
			if datetime.now() < created_at.replace(tzinfo=None)+timedelta(days=1):
				isInit = True
				date = str(created_at.replace(tzinfo=None)+timedelta(days=1)).split(' ')[0]
				message = f'Your plan will be downgraded and limited on {date}, to keep all existing features, you must select a plan before this date.'
			else:
				isPlan = False
		else:
			planid = Subscription.objects.filter(djstripe_id=subid).last().plan_id
			productid = Plan.objects.filter(djstripe_id=planid).last().product_id
			planname = Product.objects.filter(djstripe_id=productid).last().name
			current_period_end = Subscription.objects.filter(djstripe_id=subid).last().current_period_end
			if datetime.now() > current_period_end.replace(tzinfo=None):
				starterid = Plan.objects.filter(interval='month', amount=0).last().djstripe_id
				Subscription.objects.filter(djstripe_id=subid).update(plan_id=starterid)
				isAutoDown = True
		
	return Response({'isPlan':isPlan, 'planname':planname, 'isInit':isInit, 'isAutoDown':isAutoDown, 'message':message, 'currentrole':currentrole.data})
