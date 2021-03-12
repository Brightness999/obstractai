import urllib, xmltodict, json
import numpy as np

from urllib.parse import urlencode
from cyobstract import extract
from celery import shared_task
from celery import Celery
from celery_progress.backend import ProgressRecorder
from celery.schedules import crontab
from datetime import datetime, timedelta
from django.conf import settings

from pega.celery import app
from .models import (IntelGroups, Feeds, FeedItems, FeedChannels, Indicators, GlobalIndicators, IntelReports, WebHooks, GroupFeeds)

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
        groupids = []
        for groupfeed in GroupFeeds.objects.filter(feed_id=feed.id).all():
            groupids.append(groupfeed.intelgroup_id)
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
            latest_date = FeedItems.objects.filter(feed_id=feed.id).order_by('pubdate').first().pubdate
            for feeditem in FeedItems.objects.filter(feed_id=feed.id).order_by('pubdate').all():
                if datetime.strptime(latest_date, '%a, %d %b %Y %H:%M:%S %z') < datetime.strptime(feeditem.pubdate, '%a, %d %b %Y %H:%M:%S %z'):
                    latest_date = feeditem.pubdate
            for items in xmltodict.parse(contents)['rss']['channel']['item']:
                flag = False
                if feedcreated:
                    flag = True
                else:
                    if datetime.strptime(items['pubDate'], '%a, %d %b %Y %H:%M:%S %z') > datetime.strptime(latest_date, '%a, %d %b %Y %H:%M:%S %z'):
                        flag = True
                    # itemid = itemids[0].id
                    # FeedItems.objects.filter(id=itemid).update(updated_at=datetime.now())
                    # IntelReports.objects.filter(feeditem_id=itemid).order_by('id').all().update(updated_at=datetime.now())
                    # temp = np.array(itemids)
                    # itemids = temp[1:]
                if flag:
                    FeedItems.objects.create(feed_id=feed.id)
                    itemid = FeedItems.objects.last().id
                    IntelReports.objects.create(feeditem_id=itemid)
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
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'ipv4cidr' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv4 CIDR', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'ipv4range' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv4 range', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'ipv6addr' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'ipv6cidr' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6 CIDR', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'ipv6range' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6 CIDR', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'md5' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Hash', type_api='hash', value='MD5', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'sha1' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Hash', type_api='hash', value='SHA1', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'sha256' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Hash', type_api='hash', value='SHA256', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'ssdeep' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Hash', type_api='hash', value='Ssdeep', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'fqdn' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='System', type_api='system', value='FQDN', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'url' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='System', type_api='system', value='URL', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'useragent' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='System', type_api='system', value='User Agent', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'email' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='System', type_api='system', value='Email Address', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'filename' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='System', type_api='system', value='Filename', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'filepath' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='System', type_api='system', value='Filepath', value_api=result)
                                        temp = []
                                        for re in results[result]:
                                            if '\t' in re or '\n' in re or r'\u20' in re:
                                                temp = list(results[result]).remove(re)
                                        if temp != None:
                                            if temp != []:
                                                Indicators.objects.create(value=','.join(temp), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'regkey' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='System', type_api='system', value='Registry Key', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'asn' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ASN', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'asnown' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ASN Owner', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'country' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='Country', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'isp' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ISP', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'cve' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='CVE', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'malware' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Malware', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'attacktype' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Attack Type', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'incident' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Incident', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                                elif result == 'topic' and len(results[result])>0:
                                    if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                        GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Topic', value_api=result)
                                    Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
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
                            FeedItems.objects.filter(id=itemid).update(pubdate=items[item])
                        elif(item == 'source'):
                            FeedItems.objects.filter(id=itemid).update(source=items[item])
                    for groupid in groupids:
                        isSuccess = True
                        while isSuccess:
                            if len(WebHooks.objects.filter(intelgroup_id=groupid, isenable=True).order_by('id').all()) > 0:
                                for webhook in WebHooks.objects.filter(intelgroup_id=groupid, isenable=True).order_by('id').all():
                                    channelunique = FeedChannels.objects.filter(feed_id=feed.id).last().uniqueid
                                    groupunique = IntelGroups.objects.filter(id=groupid).last().uniqueid
                                    data = {
                                        'uuid': webhook.uniqueid,
                                        'channel': channelunique,
                                        'intelgroup': groupunique,
                                        'reporturl': f"{settings.SITE_ROOT_URL}/app/intelreport/"+str(IntelReports.objects.last().uniqueid),
                                        'addedtime': IntelReports.objects.filter(feeditem_id=FeedItems.objects.last().id).last().created_at,
                                        'data': {
                                            'title': FeedItems.objects.last().title,
                                            'link': FeedItems.objects.last().link,
                                            'description': FeedItems.objects.last().description
                                        }
                                    }
                                    if webhook.words == '':
                                        try:
                                            response = requests.post(webhook.endpoint, data=data)
                                            if response.status_code >= 500:
                                                isSuccess = False
                                        except Exception as e:
                                            print(str(e))
                                            isSuccess = False
                                    else:
                                        isExist = False
                                        for word in webhook.words.split(','):
                                            if word.strip() in FeedItems.objects.last().title:
                                                isExist = True
                                            if word.strip() in FeedItems.objects.last().title:
                                                isExist = True
                                        if isExist:
                                            try:
                                                response = requests.post(webhook.endpoint, data=data)
                                                if response.status_code >= 500:
                                                    isSuccess = False
                                            except Exception as e:
                                                print(str(e))
                                                isSuccess = False
                                        else:
                                            isSuccess = False
                            else:
                                isSuccess = False
        if type(xmltodict.parse(contents)['rss']['channel']['item']) is not list:
            latest_date = FeedItems.objects.filter(feed_id=feed.id).order_by('pubdate').first().pubdate
            for feeditem in FeedItems.objects.filter(feed_id=feed.id).order_by('pubdate').all():
                if datetime.strptime(latest_date, '%a, %d %b %Y %H:%M:%S %z') < datetime.strptime(feeditem.pubdate, '%a, %d %b %Y %H:%M:%S %z'):
                    latest_date = feeditem.pubdate
            flag = False
            if len(FeedItems.objects.filter(feed_id=feed.id).all()) == 0:
                flag = True
            else:
                if datetime.strptime(xmltodict.parse(contents)['rss']['channel']['item']['pubDate'], '%a, %d %b %Y %H:%M:%S %z') > datetime.strptime(latest_date, '%a, %d %b %Y %H:%M:%S %z'):
                    flag = True
            if flag:
                FeedItems.objects.create(feed_id=feed.id)
                itemid = FeedItems.objects.last().id
                IntelReports.objects.create(feeditem_id=itemid)
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
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'ipv4cidr' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv4 CIDR', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'ipv4range' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv4 range', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'ipv6addr' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'ipv6cidr' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6 CIDR', value_api=result)
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6 CIDR', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'ipv6range' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6 CIDR', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'md5' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Hash', type_api='hash', value='MD5', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'sha1' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Hash', type_api='hash', value='SHA1', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'sha256' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Hash', type_api='hash', value='SHA256', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'ssdeep' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Hash', type_api='hash', value='Ssdeep', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'fqdn' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='System', type_api='system', value='FQDN', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'url' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='System', type_api='system', value='URL', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'useragent' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='System', type_api='system', value='User Agent', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'email' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='System', type_api='system', value='Email Address', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'filename' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='System', type_api='system', value='Filename', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'filepath' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='System', type_api='system', value='Filepath', value_api=result)
                                    temp = []
                                    for re in results[result]:
                                        if '\t' in re or '\n' in re or r'\u20' in re:
                                            temp = list(results[result]).remove(re)
                                    if temp != None:
                                        if temp != []:
                                            Indicators.objects.create(value=','.join(temp), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'regkey' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='System', type_api='system', value='Registry Key', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'asn' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ASN', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'asnown' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ASN Owner', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'country' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='Country', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'isp' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ISP', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'cve' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='CVE', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'malware' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Malware', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'attacktype' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Attack Type', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'incident' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Incident', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            elif result == 'topic' and len(results[result])>0:
                                if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
                                    GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Topic', value_api=result)
                                Indicators.objects.create(value=','.join(results[result]), feeditem_id=itemid, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).last().id, isenable=True)
                            else:
                                print('indicator->', result)
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
            for groupid in groupids:
                isSuccess = True
                while isSuccess:
                    if len(WebHooks.objects.filter(intelgroup_id=groupid, isenable=True).order_by('id').all()) > 0:
                        for webhook in WebHooks.objects.filter(intelgroup_id=groupid, isenable=True).order_by('id').all():
                            channelunique = FeedChannels.objects.filter(feed_id=feed.id).last().uniqueid
                            groupunique = IntelGroups.objects.filter(id=groupid).last().uniqueid
                            data = {
                                'uuid': webhook.uniqueid,
                                'channel': channelunique,
                                'intelgroup': groupunique,
                                'reporturl': f"{settings.SITE_ROOT_URL}/app/intelreport/"+str(IntelReports.objects.last().id),
                                'addedtime': IntelReports.objects.filter(feeditem_id=FeedItems.objects.last().id).last().created_at,
                                'data': {
                                    'title': FeedItems.objects.last().title,
                                    'link': FeedItems.objects.last().link,
                                    'description': FeedItems.objects.last().description
                                }
                            }
                            if webhook.words == '':
                                try:
                                    response = requests.post(webhook.endpoint, data=data)
                                    if response.status_code >= 500:
                                        isSuccess = False
                                except Exception as e:
                                    print(str(e))
                                    isSuccess = False
                            else:
                                isExist = False
                                for word in webhook.words.split(','):
                                    if word.strip() in FeedItems.objects.last().title:
                                        isExist = True
                                    if word.strip() in FeedItems.objects.last().title:
                                        isExist = True
                                if isExist:
                                    try:
                                        response = requests.post(webhook.endpoint, data=data)
                                        if response.status_code >= 500:
                                            isSuccess = False
                                    except Exception as e:
                                        print(str(e))
                                        isSuccess = False
                                else:
                                    isSuccess = False
                    else:
                        isSuccess = False

    return 'done'



