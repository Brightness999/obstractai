import os
import urllib
import xmltodict
import json

from cyobstract import extract
from django.contrib import admin, messages
from django.core.exceptions import ValidationError

# Register your models here.
from .models import *
import djstripe, stripe

@admin.register(Feeds)
class FeedAdmin(admin.ModelAdmin):
	list_display = ('id', 'url', 'name', 'description', 'category', 'tags')
	readonly_fields = ('intelgroup',)
	def save_model(self, request, obj, form, change):
		flag = True
		for feed in Feeds.objects.all():
			if form.cleaned_data['url'] in feed.url:
				flag = False
		if flag:
			super().save_model(request, obj, form, change)
			for tag in form.cleaned_data['tags'].split(','):
				flag = False
				for existingtag in Tags.objects.all():
					if tag.strip() == existingtag.name:
						flag = True
				if not flag:
					Tags.objects.create(name=tag.strip(), isglobal=True)
			if not change:
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
												GlobalIndicators.objects.create(type='System', type_api='system', value='Filepath', value_api=result)
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
													GlobalIndicators.objects.create(type='System', type_api='system', value='Filepath', value_api=result)
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
											GlobalIndicators.objects.create(type='Infrastructure', type_api='infrastructure', value='country', value_api=result)
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
											GlobalIndicators.objects.create(type='Analysis', type_api='analysis', value='Attack type', value_api=result)
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
			return True
		else:
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
			new_product=stripe.Product.create(
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
			stripe.Plan.create(
				amount=form.cleaned_data['weekly_amount'],
				currency="usd",
				interval="week",
				product=new_product.id,
				billing_scheme="per_unit",
				interval_count=1
			)
			stripe.Plan.create(
				amount=form.cleaned_data['daily_amount'],
				currency="usd",
				interval="day",
				product=new_product.id,
				billing_scheme="per_unit",
				interval_count=1
			)
		return True

@admin.register(IntelReports)
class IntelReportsAdmin(admin.ModelAdmin):
	def has_add_permission(self, request, obj=None):
		return False