import secrets
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.users.models import CustomUser
from ..models import IntelGroups, APIKeys, WebHooks, UserIntelGroupRoles, Extractions, FeedChannels, FeedItems, Feeds, Categories, UserIntelGroupRoles, Indicators, Tags, GlobalIndicators
from ..serializers import RoleGroupSerializer, UserSerializer, GroupAPIkeySerializer, GroupWebHookSerializer, FeedCategorySerializer, CategorySerializer, FeedItemSerializer, UserExtractionSerializer, UserExtractionSerializer, ItemIndicatorSerializer, FeedChannelSerializer, TagSerializer, GlobalIndicatorSerializer

def home(request):
        return render(request, 'project/index.html')

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

@api_view(['POST'])
def apikeys(request):
	key = secrets.token_urlsafe(16)
	APIKeys.objects.create(name=request.data['name'], intelgroup_id=request.data['intelgroup_id'], value=key, user_id=request.user.id)
	apikeys = []
	for apikey in APIKeys.objects.all():
		serializer = GroupAPIkeySerializer(apikey)
		apikeys.append(serializer.data)
		
	return Response(apikeys)

@api_view(['POST'])
def webhooks(request):
	WebHooks.objects.create(endpoint=request.data['endpoint'], description=request.data['description'], intelgroup_id=request.data['intelgroup_id'], user_id=request.user.id)
	webhooks = []
	for webhook in WebHooks.objects.all():
		serializer = GroupWebHookSerializer(webhook)
		webhooks.append(serializer.data)
	
	return Response(webhooks)

@api_view(['PUT'])
def webhooks(request):
	WebHooks.objects.filter(id=request.data['id']).update(endpoint=request.data['endpoint'], description=request.data['description'], intelgroup_id=request.data['intelgroup_id'], user_id=request.user.id)
	webhooks = []
	for webhook in WebHooks.objects.all():
		serializer = GroupWebHookSerializer(webhook)
		webhooks.append(serializer.data)
	
	return Response(webhooks)

@api_view(['DELETE'])
def webhooks(request):
	WebHooks.objects.filter(id=request.data['id']).delete()
	webhooks = []
	for webhook in WebHooks.objects.all():
		serializer = GroupWebHookSerializer(webhook)
		webhooks.append(serializer.data)
	
	return Response(webhooks)

@api_view(['GET'])
def reports(request):
	feeds = []
	groupids = []
	feedids = []
	feedchannels = []
	feeditems =[]
	indicators = []
	extractions = []
	categories = []
	itemids = []
	tags = []
	globalindicators = [];
	for role in UserIntelGroupRoles.objects.order_by('id').filter(user_id=request.user.id).all():
		groupids.append(role.intelgroup_id)
	for feed in Feeds.objects.order_by('id').filter(intelgroup_id__in=groupids).all():
		serializer = FeedCategorySerializer(feed)
		feeds.append(serializer.data)
		feedids.append(feed.id)
	for channel in FeedChannels.objects.filter(feed_id__in=feedids).order_by('id').all():
		serializer = FeedChannelSerializer(channel)
		feedchannels.append(serializer.data)
	for item in FeedItems.objects.filter(feed_id__in=feedids).order_by('id').all():
		serializer = FeedItemSerializer(item)
		feeditems.append(serializer.data)
		itemids.append(item.id)
	for indicator in Indicators.objects.filter(feeditem_id__in=itemids).order_by('id').all():
		serializer = ItemIndicatorSerializer(indicator)
		indicators.append(serializer.data)
	for extraction in Extractions.objects.filter(intelgroup_id__in=groupids):
		serializer = UserExtractionSerializer(extraction)
		extractions.append(serializer.data)
	for category in Categories.objects.order_by('id').all():
		serializer = CategorySerializer(category)
		categories.append(serializer.data)
	for tag in Tags.objects.filter(Q(state='global') | Q(user_id=request.user.id)).order_by('id').all():
		serializer = TagSerializer(tag)
		tags.append(serializer.data)
	for globalindicator in GlobalIndicators.objects.all():
		serializer = GlobalIndicatorSerializer(globalindicator)
		globalindicators.append(serializer.data)

	return Response({'feeds':feeds, 'feedchannels':feedchannels, 'feeditems':feeditems, 'indicators':indicators, 'extractions':extractions, 'categories':categories, 'tags':tags, 'globalindicators':globalindicators})

@api_view(['POST'])
def searchreports(request):
	# print(request.data)
	# if request.data['category'] != '0'
	return Response(request.data)
	