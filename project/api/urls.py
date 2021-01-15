from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'api'
urlpatterns = [
    path(r'v1/feeds', views.apifeeds, name='apifeeds'),
    path(r'v1/reports', views.apireports, name='apireports'),
    path(r'v1/intel_group', views.apigroups, name='apigroups'),
    path(r'home', views.home, name='home'),
    path(r'account', views.account, name='account'),
    path(r'changingemail', views.emailchange, name='email'),
    path(r'apikeys', views.apikeys, name='apikeys'),
    path(r'webhooks', views.webhooks, name='webhooks'),
    path(r'reports', views.reports, name='reports'),
    path(r'searchreports', views.searchreports, name='searchreports'),
    path(r'feeds', views.feeds, name='feeds'),
    path(r'feedlist', views.feedlist, name='feedlist'),
    path(r'attributes', views.attributes, name='attributes'),
    path(r'whitelist', views.whitelist, name='whitelist'),
    path(r'indicators', views.indicators, name='indicators'),
    path(r'invite', views.invite, name='invite'),
    path(r'currentrole', views.currentrole, name='currentrole'),
    path(r'categories', views.categories, name='categories'),
    path(r'globalindicators', views.globalindicators, name='globalindicators'),
    path(r'globalattributes', views.globalattributes, name='globalattributes'),

]
