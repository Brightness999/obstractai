import re
import urllib

from urllib.parse import urlencode
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import xmltodict
import pprint
import json
from cyobstract import extract

from ..models import Feeds, FeedChannels, FeedItems, Indicators, GlobalIndicators, UserIntelGroupRoles
from ..serializers import FeedCategorySerializer, FeedSerializer

@method_decorator(login_required, name='dispatch')
class FeedViewSet(viewsets.ModelViewSet):
    queryset = Feeds.objects.all()
    serializer_class = FeedCategorySerializer

    def get_queryset(self):
        groupids = []
        for role in UserIntelGroupRoles.objects.filter(user_id=self.request.user.id).order_by('id').all():
            groupids.append(role.intelgroup_id)
        print(groupids)
        feeds = Feeds.objects.filter(intelgroup_id__in=groupids).order_by('id').all()
        return feeds
    def partial_update(self,request, pk):
        groupids = []
        for role in UserIntelGroupRoles.objects.filter(user_id=request.user.id).order_by('id').all():
            groupids.append(role.intelgroup_id)
        Feeds.objects.filter(pk=pk).update(url=request.data['url'], category_id=request.data['category'], description=request.data['description'], name=request.data['name'], tags=request.data['tags'], manage_enabled=request.data['manage_enabled'])
        feeds = Feeds.objects.filter(intelgroup_id__in=groupids).order_by('id').all().values()
        return Response(feeds)

    @action(detail=False, methods=['POST'])
    def add(self, request):
        feeds = Feeds.objects.all()
        data=request.data
        groupid=6
        flag = True
        for feed in feeds:
            if(data['url'] in feed.url and feed.intelgroup_id == groupid):
                Feeds.objects.filter(id=feed.id).update(url=data['url'], name=data['name'], description=data['description'], category_id=data['category'], tags=data['tags'], manage_enabled='false', intelgroup_id=groupid)
                flag = False
            elif(data['url'] in feed.url and feed.intelgroup_id != groupid):
                Feeds.objects.create(uniqueid=feed.uniqueid, url=data['url'], name=data['name'], description=data['description'], category_id=data['category'], tags=data['tags'], manage_enabled='false', intelgroup_id=groupid, confidence=data['confidence'])    
                flag = False
        if(flag):
            Feeds.objects.create(url=data['url'], name=data['name'], description=data['description'], category_id=data['category'], tags=data['tags'], manage_enabled='false', intelgroup_id=groupid, confidence=data['confidence'])
            print(Feeds.objects.last().id)
            ftr = "http://ftr-premium.fivefilters.org/"
            # encode = urllib.parse.quote_plus("https://www.fcbarcelona.com/en/football/first-team/news")
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
                                print(GlobalIndicators.objects.filter(value_api=result).values()[0]['id'])
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
                                    print(GlobalIndicators.objects.filter(value_api=result).values()[0])
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
        queryset = Feeds.objects.order_by('id').all()
        serializer = FeedCategorySerializer(queryset, many=True)
        return Response(serializer.data)
    @action(detail=False, methods=['PATCH'])
    def search(self, request):
        data = [];
        if(request.data['category'] == '' and request.data['tags'] == ''):
            data = Feeds.objects.order_by('id').all()
        if(request.data['category'] != '' and request.data['tags'] == ''):
            data = Feeds.objects.order_by('id').filter(category_id = request.data['category']).all()
        if(request.data['category'] == '' and request.data['tags'] != ''):
            feedlist = Feeds.objects.all()
            for feed in feedlist:
                if(request.data['tags'] in feed.tags):
                    data.append(feed)
        if(request.data['category'] != '' and request.data['tags'] != ''):
            temp = Feeds.objects.order_by('id').filter(category_id = request.data['category']).all()
            for t in temp:
                if(request.data['tags'] in t.tags):
                    data.append(t)
        result = []
        for d in data:
            serializer = FeedCategorySerializer(d)
            result.append(serializer.data)
        return Response(result)
