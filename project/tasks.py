import urllib, xmltodict, json
import numpy as np

from urllib.parse import urlencode
from cyobstract import extract
from celery import shared_task
from celery import Celery
from celery_progress.backend import ProgressRecorder
from celery.schedules import crontab
from datetime import datetime, timedelta

from pega.celery import app
from .models import (IntelGroups, Feeds, FeedItems, FeedChannels, Indicators, GlobalIndicators, IntelReports, WebHooks)

@app.task(bind=True)
def feed(self):
    feeds = Feeds.objects.order_by('id').all()
    feeds.update(updated_at=datetime.now())
    for feed in Feeds.objects.order_by('id').all():
        ftr = "http://ftr-premium.fivefilters.org/"
        encode = urllib.parse.quote_plus(feed.url)
        key = urllib.parse.quote_plus("KSF8GH22GZRKA8")
        req = urllib.request.Request(ftr+"makefulltextfeed.php?url="+encode+"&key="+key+"&max=25")
        contents = urllib.request.urlopen(req).read()
        channelid = 0
        feedcreated = False
        if len(FeedChannels.objects.filter(feed_id=feed.id).all()) == 0:
            FeedChannels.objects.create(feed_id=feed.id)
            channelid = FeedChannels.objects.last().id
            feedcreated = True
        else:
            channelid = FeedChannels.objects.filter(feed_id=feed.id).last().id
            FeedChannels.objects.filter(id=channelid).update(updated_at=datetime.now())
        
        for item in xmltodict.parse(contents)['rss']['channel']:
            if(item == 'title'):
                FeedChannels.objects.filter(id=channelid).update(title=xmltodict.parse(contents)['rss']['channel'][item])
            elif(item == 'link'):
                FeedChannels.objects.filter(id=channelid).update(link=xmltodict.parse(contents)['rss']['channel'][item])
            elif(item == 'description'):
                FeedChannels.objects.filter(id=channelid).update(description=xmltodict.parse(contents)['rss']['channel'][item])
            elif(item == 'language'):
                FeedChannels.objects.filter(id=channelid).update(language=xmltodict.parse(contents)['rss']['channel'][item])
            elif(item == 'copyright'):
                FeedChannels.objects.filter(id=channelid).update(copyright=xmltodict.parse(contents)['rss']['channel'][item])
            elif(item == 'managingeditor'):
                FeedChannels.objects.filter(id=channelid).update(managingeditor=xmltodict.parse(contents)['rss']['channel'][item])
            elif(item == 'webmaster'):
                FeedChannels.objects.filter(id=channelid).update(webmaster=xmltodict.parse(contents)['rss']['channel'][item])
            elif(item == 'pubDate'):
                FeedChannels.objects.filter(id=channelid).update(pubdate=xmltodict.parse(contents)['rss']['channel'][item])
            elif(item == 'category'):
                FeedChannels.objects.filter(id=channelid).update(category=xmltodict.parse(contents)['rss']['channel'][item])
            elif(item == 'lastbuilddate'):
                FeedChannels.objects.filter(id=channelid).update(lastbuilddate=xmltodict.parse(contents)['rss']['channel'][item])
            elif(item == 'generator'):
                FeedChannels.objects.filter(id=channelid).update(generator=xmltodict.parse(contents)['rss']['channel'][item])
            elif(item == 'docs'):
                FeedChannels.objects.filter(id=channelid).update(docs=xmltodict.parse(contents)['rss']['channel'][item])
            elif(item == 'cloud'):
                FeedChannels.objects.filter(id=channelid).update(cloud=xmltodict.parse(contents)['rss']['channel'][item])
            elif(item == 'ttl'):
                FeedChannels.objects.filter(id=channelid).update(ttl=xmltodict.parse(contents)['rss']['channel'][item])
            elif(item == 'image'):
                FeedChannels.objects.filter(id=channelid).update(image=xmltodict.parse(contents)['rss']['channel'][item])
            elif(item == 'textinput'):
                FeedChannels.objects.filter(id=channelid).update(textinput=xmltodict.parse(contents)['rss']['channel'][item])
            elif(item == 'skiphours'):
                FeedChannels.objects.filter(id=channelid).update(skiphours=xmltodict.parse(contents)['rss']['channel'][item])
            elif(item == 'skipdays'):
                FeedChannels.objects.filter(id=channelid).update(skipdays=xmltodict.parse(contents)['rss']['channel'][item])
        if type(xmltodict.parse(contents)['rss']['channel']['item']) is list:
            for items in xmltodict.parse(contents)['rss']['channel']['item']:
                flag = False
                if feedcreated:
                    FeedItems.objects.create(feed_id=feed.id)
                    flag = True
                else:
                    for feeditem in FeedItems.objects.filter(feed_id=feed.id).order_by('id').all():
                        if items['pubDate'].date() > feeditem.pubdate.date():
                            if(feed.id==38):
                                print(feeditem.id)
                                print(feeditem.pubdate)
                                print(items['pubDate'])
                            # FeedItems.objects.create(feed_id=feed.id)
                            flag = True
                    # itemid = itemids[0].id
                    # FeedItems.objects.filter(id=itemid).update(updated_at=datetime.now())
                    # IntelReports.objects.filter(feeditem_id=itemid).order_by('id').all().update(updated_at=datetime.now())
                    # temp = np.array(itemids)
                    # itemids = temp[1:]
                itemid = FeedItems.objects.last().id
                if flag:
                    for item in items:
                        if(item == 'title'):
                            FeedItems.objects.filter(id=itemid).update(title=items[item])
                        elif(item == 'link'):
                            FeedItems.objects.filter(id=itemid).update(link=items[item])
                        elif(item == 'description'):
                            FeedItems.objects.filter(id=itemid).update(description=items[item])
                            text = json.dumps(items[item])
                            results = extract.extract_observables(text)
                            for result in results:
                                if result == 'ipv4addr' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                            GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv4', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'ipv4cidr' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv4 CIDR', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'ipv4range' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv4 range', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'ipv6addr' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'ipv6cidr' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6 CIDR', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'ipv6range' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6 CIDR', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'md5' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Hash', type_api='hash', value='MD5', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'sha1' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Hash', type_api='hash', value='SHA1', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'sha256' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Hash', type_api='hash', value='SHA256', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'ssdeep' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Hash', type_api='hash', value='Ssdeep', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'fqdn' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='System', type_api='system', value='FQDN', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'url' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='System', type_api='system', value='URL', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'useragent' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='System', type_api='system', value='User Agent', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'email' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='System', type_api='system', value='Email Address', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'filename' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='System', type_api='system', value='Filename', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'filepath' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='System', type_api='system', value='Filepath', value_api=result)
                                    if feedcreated:
                                        temp = []
                                        for re in results[result]:
                                            if '\t' in re or '\n' in re or r'\u20' in re:
                                                temp = list(results[result]).remove(re)
                                        if temp != None:
                                            if temp != []:
                                                temp.reverse()
                                                Indicators.objects.create(value=','.join(temp), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'regkey' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='System', type_api='system', value='Registry Key', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'asn' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ASN', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'asnown' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ASN Owner', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'country' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='Country', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'isp' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ISP', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'cve' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='CVE', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'malware' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Malware', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'attacktype' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Attack Type', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'incident' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Incident', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                elif result == 'topic' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Topic', value_api=result)
                                    if feedcreated:
                                        Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                    else:
                                        Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                                # else:
                                #     print('indicator->', result)
                        elif(item == 'author'):
                            FeedItems.objects.filter(id=itemid).update(author=items[item])
                        elif(item == 'category'):
                            FeedItems.objects.filter(id=itemid).update(category=items[item])
                        elif(item == 'comments'):
                            FeedItems.objects.filter(id=itemid).update(comments=items[item])
                        elif(item == 'enclosure'):
                            FeedItems.objects.filter(id=itemid).update(enclosure=items[item])
                        elif(item == 'guid'):
                            FeedItems.objects.filter(id=itemid).update(guid=items[item])
                        elif(item == 'pubDate'):
                            print('pubdate')
                            FeedItems.objects.filter(id=itemid).update(pubdate=items[item])
                        elif(item == 'source'):
                            FeedItems.objects.filter(id=itemid).update(source=items[item])
            
        if type(xmltodict.parse(contents)['rss']['channel']['item']) is not list:
            flag = False
            if len(FeedItems.objects.filter(feed_id=feed.id).all()) == 0:
                FeedItems.objects.create(feed_id=feed.id)
                flag = True
            else:
                for feeditem in FeedItems.objects.filter(feed_id=feed.id).order_by('id').all():
                    # print(xmltodict.parse(contents)['rss']['channel']['item']['pubDate'])
                    # print(feeditem.pubdate)
                    if xmltodict.parse(contents)['rss']['channel']['item']['pubDate'] > feeditem.pubdate:
                        flag = True
                # itemid = FeedItems.objects.filter(feed_id=feed.id).last().id
                # FeedItems.objects.filter(id=itemid).update(updated_at=datetime.now())
                # IntelReports.objects.filter(feeditem_id=itemid).order_by('id').all().update(updated_at=datetime.now())
            itemid = FeedItems.objects.last().id
            if flag:
                for item in xmltodict.parse(contents)['rss']['channel']['item']:
                    if(item == 'title'):
                        FeedItems.objects.filter(id=itemid).update(title=xmltodict.parse(contents)['rss']['channel']['item'][item])
                    elif(item == 'link'):
                        FeedItems.objects.filter(id=itemid).update(link=xmltodict.parse(contents)['rss']['channel']['item'][item])
                    elif(item == 'description'):
                        FeedItems.objects.filter(id=itemid).update(description=xmltodict.parse(contents)['rss']['channel']['item'][item])
                        text = json.dumps(xmltodict.parse(contents)['rss']['channel']['item'][item])
                        results = extract.extract_observables(text)
                        for result in results:
                            if result == 'ipv4addr' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv4', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'ipv4cidr' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv4 CIDR', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'ipv4range' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv4 range', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'ipv6addr' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'ipv6cidr' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6 CIDR', value_api=result)
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6 CIDR', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'ipv6range' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6 CIDR', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'md5' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Hash', type_api='hash', value='MD5', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'sha1' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Hash', type_api='hash', value='SHA1', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'sha256' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Hash', type_api='hash', value='SHA256', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'ssdeep' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Hash', type_api='hash', value='Ssdeep', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'fqdn' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='System', type_api='system', value='FQDN', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'url' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='System', type_api='system', value='URL', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'useragent' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='System', type_api='system', value='User Agent', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'email' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='System', type_api='system', value='Email Address', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'filename' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='System', type_api='system', value='Filename', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'filepath' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='System', type_api='system', value='Filepath', value_api=result)
                                if feedcreated:
                                    temp = []
                                    for re in results[result]:
                                        if '\t' in re or '\n' in re or r'\u20' in re:
                                            temp = list(results[result]).remove(re)
                                    if temp != None:
                                        if temp != []:
                                            temp.reverse()
                                            Indicators.objects.create(value=','.join(temp), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'regkey' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='System', type_api='system', value='Registry Key', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'asn' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ASN', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'asnown' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ASN Owner', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'country' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='Country', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'isp' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ISP', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'cve' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='CVE', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'malware' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Malware', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'attacktype' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Attack Type', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'incident' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Incident', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            elif result == 'topic' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Topic', value_api=result)
                                if feedcreated:
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                else:
                                    Indicators.objects.filter(feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id).update(value=','.join(results[result]), isenable=True)
                            # else:
                            #     print('indicator->', result)
                    elif(item == 'author'):
                        FeedItems.objects.filter(id=itemid).update(author=xmltodict.parse(contents)['rss']['channel']['item'][item])
                    elif(item == 'category'):
                        FeedItems.objects.filter(id=itemid).update(category=xmltodict.parse(contents)['rss']['channel']['item'][item])
                    elif(item == 'comments'):
                        FeedItems.objects.filter(id=itemid).update(comments=xmltodict.parse(contents)['rss']['channel']['item'][item])
                    elif(item == 'enclosure'):
                        FeedItems.objects.filter(id=itemid).update(enclosure=xmltodict.parse(contents)['rss']['channel']['item'][item])
                    elif(item == 'guid'):
                        FeedItems.objects.filter(id=itemid).update(guid=xmltodict.parse(contents)['rss']['channel']['item'][item])
                    elif(item == 'pubDate'):
                        FeedItems.objects.filter(id=itemid).update(pubdate=xmltodict.parse(contents)['rss']['channel']['item'][item])
                    elif(item == 'source'):
                        FeedItems.objects.filter(id=itemid).update(source=xmltodict.parse(contents)['rss']['channel']['item'][item])
                
    return 'done'



