import secrets
import urllib
import xmltodict
import json

from urllib.parse import urlencode
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from rest_framework.decorators import api_view
from rest_framework.response import Response
from cyobstract import extract

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
	apikeys = []
	key = secrets.token_urlsafe(16)
	APIKeys.objects.create(name=request.data['name'], intelgroup_id=request.data['intelgroup_id'], value=key, user_id=request.user.id)
	for apikey in APIKeys.objects.filter(user_id=request.user.id).all():
		serializer = GroupAPIkeySerializer(apikey)
		apikeys.append(serializer.data)
		
	return Response(apikeys)

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
		WebHooks.objects.filter(id=request.data['id']).update(endpoint=request.data['endpoint'], description=request.data['description'], intelgroup_id=request.data['intelgroup_id'], user_id=request.user.id)
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

@api_view(['GET'])
def reports(request):
	feeds = []
	groupids = []
	feedids = []
	myfeedids = []
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
		# feedids.append(feed.id)
		feedids.append(Feeds.objects.filter(uniqueid=feed.uniqueid).order_by('id').first().id)
		print(myfeedids)
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

@api_view(['POST'])
def feeds(request):
	data=request.data
	groupid= request.data['intelgroup_id']
	isUrlExist = False
	isEqualGroup = False
	for feed in Feeds.objects.all():
		if(data['url'] in feed.url):
			isUrlExist = True
			if feed.intelgroup_id == groupid:
				isEqualGroup = True
				Feeds.objects.filter(id=feed.id).update(url=data['url'], name=data['name'], description=data['description'], category_id=data['category'], tags=data['tags'], manage_enabled='false', intelgroup_id=groupid)
	if isUrlExist and not isEqualGroup:
		Feeds.objects.create(uniqueid=Feeds.objects.filter(url=data['url']).order_by('id').first().uniqueid, url=data['url'], name=data['name'], description=data['description'], category_id=data['category'], tags=data['tags'], manage_enabled='false', intelgroup_id=groupid, confidence=data['confidence'])    
		isUrlExist = True
	if not isUrlExist:
		Feeds.objects.create(url=data['url'], name=data['name'], description=data['description'], category_id=data['category'], tags=data['tags'], manage_enabled='false', intelgroup_id=groupid, confidence=data['confidence'])
		ftr = "http://ftr-premium.fivefilters.org/"
		encode = urllib.parse.quote_plus(data['url'])
		req = urllib.request.Request(ftr+"makefulltextfeed.php?url="+encode+"&key=KSF8GH22GZRKA8")
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
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif result == 'ipv4cidr' and len(results[result])>0:
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif result == 'ipv4range' and len(results[result])>0:
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif result == 'ipv6addr' and len(results[result])>0:
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif result == 'ipv6cidr' and len(results[result])>0:
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif result == 'ipv6range' and len(results[result])>0:
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif result == 'md5' and len(results[result])>0:
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif result == 'sha1' and len(results[result])>0:
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif result == 'sha256' and len(results[result])>0:
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif result == 'ssdeep' and len(results[result])>0:
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif result == 'fqdn' and len(results[result])>0:
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif result == 'url' and len(results[result])>0:
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif result == 'useragent' and len(results[result])>0:
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif result == 'email' and len(results[result])>0:
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif result == 'filename' and len(results[result])>0:
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif result == 'filepath' and len(results[result])>0:
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif result == 'regkey' and len(results[result])>0:
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif result == 'asn' and len(results[result])>0:
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif result == 'asnown' and len(results[result])>0:
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif result == 'country' and len(results[result])>0:
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif result == 'isp' and len(results[result])>0:
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif result == 'cve' and len(results[result])>0:
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif result == 'malware' and len(results[result])>0:
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
						elif result == 'attacktype' and len(results[result])>0:
							Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
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
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'ipv4cidr' and len(results[result])>0:
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'ipv4range' and len(results[result])>0:
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'ipv6addr' and len(results[result])>0:
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'ipv6cidr' and len(results[result])>0:
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'ipv6range' and len(results[result])>0:
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'md5' and len(results[result])>0:
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'sha1' and len(results[result])>0:
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'sha256' and len(results[result])>0:
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'ssdeep' and len(results[result])>0:
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'fqdn' and len(results[result])>0:
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'url' and len(results[result])>0:
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'useragent' and len(results[result])>0:
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'email' and len(results[result])>0:
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'filename' and len(results[result])>0:
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'filepath' and len(results[result])>0:
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'regkey' and len(results[result])>0:
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'asn' and len(results[result])>0:
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'asnown' and len(results[result])>0:
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'country' and len(results[result])>0:
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'isp' and len(results[result])>0:
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'cve' and len(results[result])>0:
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'malware' and len(results[result])>0:
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
							elif result == 'attacktype' and len(results[result])>0:
								Indicators.objects.create(value=results[result], feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], enabled='Enable')
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
	for role in UserIntelGroupRoles.objects.filter(user_id=request.user.id).order_by('id').all():
		groupids.append(role.intelgroup_id)
	queryset = Feeds.objects.filter(intelgroup_id__in=groupids).order_by('id').all()
	serializer = FeedCategorySerializer(queryset, many=True)
	return Response(serializer.data)
