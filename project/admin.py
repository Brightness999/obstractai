import os
import urllib
import xmltodict
import json
from datetime import datetime

import djstripe
from cyobstract import extract
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django import forms

# Register your models here.
from .models import *
import djstripe, stripe
from djstripe.models import Plan, Product

@admin.register(Feeds)
class FeedAdmin(admin.ModelAdmin):
	list_display = ('id', 'url', 'name', 'description', 'category', 'tags')
	def save_model(self, request, obj, form, change):
		super().save_model(request, obj, form, change)
		if not change:
			count = 0
			for feed in Feeds.objects.all():
				if form.cleaned_data['url'] in feed.url:
					count += 1
			if count < 2:
				for tag in form.cleaned_data['tags'].split(','):
					flag = False
					for existingtag in Tags.objects.all():
						if tag.strip() == existingtag.name:
							flag = True
					if not flag:
						Tags.objects.create(name=tag.strip(), isglobal=True)
			
				ftr = "http://ftr-premium.fivefilters.org/"
				encode = urllib.parse.quote_plus(form.cleaned_data['url'])
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
								if result == 'ipv4addr':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv4', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'ipv4cidr':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv4 CIDR', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'ipv4range':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv4 Range', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'ipv6addr':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'ipv6cidr':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6 CIDR', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'ipv6range':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6 Range', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'md5':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='Hash', type_api='hash', value='MD5', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'sha1':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='Hash', type_api='hash', value='SHA1', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'sha256':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='Hash', type_api='hash', value='SHA256', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'ssdeep':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='Hash', type_api='hash', value='Ssdeep', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'fqdn':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='System', type_api='system', value='FQDN', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'url':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='System', type_api='system', value='URL', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'useragent':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='System', type_api='system', value='User Agent', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'email':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='System', type_api='system', value='Email Address', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'filename':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='System', type_api='system', value='Filename', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'filepath':
									temp = []
									for re in results[result]:
										if '\t' in re or '\n' in re or r'\u20' in re:
											temp = list(results[result]).remove(re)
									if temp != None:
										if temp != []:
											temp.reverse()
											if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
												globalindicator = GlobalIndicators.objects.create(type='System', type_api='system', value='Filepath', value_api=result)
												for intelgroup in IntelGroups.objects.all():
													GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(temp), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'regkey':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='System', type_api='system', value='Registry Key', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'asn':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ASN', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'asnown':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ASN Owner', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'cc':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='Country', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'isp':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ISP', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'cve':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='CVE', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'malware':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Malware', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'attacktype':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Attack Type', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'incident':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Incident', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
										Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
								elif result == 'topic':
									if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
										globalindicator = GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Topic', value_api=result)
										for intelgroup in IntelGroups.objects.all():
											GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
									if len(results[result])>0:
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
									if result == 'ipv4addr':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv4', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'ipv4cidr':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv4 CIDR', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'ipv4range':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv4 Range', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'ipv6addr':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'ipv6cidr':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6 CIDR', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'ipv6range':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='IP address', type_api='ip', value='IPv6 Range', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'md5':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='Hash', type_api='hash', value='MD5', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'sha1':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='Hash', type_api='hash', value='SHA1', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'sha256':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='Hash', type_api='hash', value='SHA256', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'ssdeep':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='Hash', type_api='hash', value='Ssdeep', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'fqdn':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='System', type_api='system', value='FQDN', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'url':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='System', type_api='system', value='URL', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'useragent':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='System', type_api='system', value='User Agent', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'email':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='System', type_api='system', value='Email Address', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'filename':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='System', type_api='system', value='Filename', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'filepath':
										temp = []
										for re in results[result]:
											if '\t' in re or '\n' in re or r'\u20' in re:
												temp = list(results[result]).remove(re)
										if temp != None:
											if temp != []:
												temp.reverse()
												if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
													globalindicator = GlobalIndicators.objects.create(type='System', type_api='system', value='Filepath', value_api=result)
													for intelgroup in IntelGroups.objects.all():
														GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(temp), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'regkey':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='System', type_api='system', value='Registry Key', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'asn':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ASN', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'asnown':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ASN Owner', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'cc':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='country', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'isp':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='ISP', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'cve':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='CVE', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'malware':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Malware', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'attacktype':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Attack type', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'incident':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Incident', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
											Indicators.objects.create(value=','.join(results[result]), feeditem_id=FeedItems.objects.last().id, globalindicator_id=GlobalIndicators.objects.filter(value_api=result).values()[0]['id'], isenable=True)
									elif result == 'topic':
										if len(GlobalIndicators.objects.filter(value_api=result).all()) == 0:
											globalindicator = GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Topic', value_api=result)
											for intelgroup in IntelGroups.objects.all():
												GroupGlobalIndicators.objects.create(intelgroup_id=intelgroup.id, globalindicator_id=globalindicator.id, isenable=True)
										if len(results[result])>0:
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
			
				return True
			else:
				super().delete_model(request, obj)
				messages.error(request,'!This url already exists.')
				return False

@admin.register(IntelGroups)
class IntelGroupAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'plan')
	readonly_fields = ('name', 'description', 'plan')
	def has_add_permission(self, request, obj=None):
		return False

@admin.register(Categories)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('id', 'name')

@admin.register(GlobalAttributes)
class AttributeAdmin(admin.ModelAdmin):
	list_display = ('id', 'attribute', 'value', 'api_attribute', 'api_value', 'words_matched')
	def save_model(self, request, obj, form, change):
		super().save_model(request, obj, form, change)
		if not change:
			for group in IntelGroups.objects.all():
				GroupGlobalAttributes.objects.create(intelgroup_id=group.id, globalattribute_id=GlobalAttributes.objects.last().id, isenable=True)
		return True

@admin.register(GroupPlan)
class GroupPlanAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'annual_amount', 'monthly_amount', 'active', 'max_users', 'max_feeds', 'custom_feeds', 'custom_observables', 'api_access' )

	def save_model(self, request, obj, form, change):
		super().save_model(request, obj, form, change)
		if not change:
			stripe.api_key = os.environ.get("STRIPE_TEST_SECRET_KEY")
			product=stripe.Product.create(
				name=form.cleaned_data['name'],
				description=form.cleaned_data['description'],
				active= form.cleaned_data['active'],
				metadata={
					'max_users':form.cleaned_data['max_users'],
					'max_feeds':form.cleaned_data['max_feeds'],
					'custom_feeds':form.cleaned_data['custom_feeds'],
					'custom_observables':form.cleaned_data['custom_observables'],
					'api_access':form.cleaned_data['api_access'],
					'group_public':form.cleaned_data['group_public']
				}
			)
			djstripe.models.Product.sync_from_stripe_data(product)
			year_plan = stripe.Plan.create(
				amount=form.cleaned_data['annual_amount']*100,
				currency="usd",
				interval="year",
				product=product.id,
				billing_scheme="per_unit",
				interval_count=1
			)
			djstripe.models.Plan.sync_from_stripe_data(year_plan)
			month_plan = stripe.Plan.create(
				amount=form.cleaned_data['monthly_amount']*100,
				currency="usd",
				interval="month",
				product=product.id,
				billing_scheme="per_unit",
				interval_count=1
			)
			djstripe.models.Plan.sync_from_stripe_data(month_plan)
			week_plan = stripe.Plan.create(
				amount=form.cleaned_data['weekly_amount']*100,
				currency="usd",
				interval="week",
				product=product.id,
				billing_scheme="per_unit",
				interval_count=1
			)
			djstripe.models.Plan.sync_from_stripe_data(week_plan)
			day_plan = stripe.Plan.create(
				amount=form.cleaned_data['daily_amount']*100,
				currency="usd",
				interval="day",
				product=product.id,
				billing_scheme="per_unit",
				interval_count=1
			)
			djstripe.models.Plan.sync_from_stripe_data(day_plan)
		return True


@admin.register(IntelReports)
class IntelReportsAdmin(admin.ModelAdmin):
	list_display = ("id", "report_name", "feed_name", "date_ingested" )
	readonly_fields = ("feeditem", "id", "report_name", "feed_name", "date_ingested" )
	
	def report_name(self, obj):
		return obj.feeditem.title
	def date_ingested(slef, obj):
		return obj.created_at
	def feed_name(self, obj):
		return obj.feeditem.feed.name

	def has_add_permission(self, request, obj=None):
		return False
	def has_delete_permission(self, request, obj=None):
		return False
	def has__permission(self, request, obj=None):
		return False
	

@admin.register(GroupFeeds)
class GroupFeedsAdmin(admin.ModelAdmin):

	list_display = ('id', 'feed', 'intelgroup', 'name', 'description', 'category', 'tags', 'confidence')

	def feed(self, obj):
		return obj.feed.id

	def has_add_permission(self, request, obj=None):
		return False
	# def has_change_permission(self, request, obj=None):
	# 	return False
	def has_delete_permission(self, request, obj=None):
		return False
	def has__permission(self, request, obj=None):
		return False