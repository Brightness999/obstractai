from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'api'
urlpatterns = [
    path(r'test', views.home, name='home'),
    path(r'account', views.account, name='account'),
    path(r'changingemail', views.emailchange, name='email'),
    path(r'apikeys', views.apikeys, name='apikeys'),
    path(r'webhooks', views.webhooks, name='webhooks'),
    path(r'reports', views.reports, name='reports'),
    path(r'searchreports', views.searchreports, name='searchreports'),
    path(r'feeds', views.feeds, name='feeds'),
    path(r'feed', views.feed, name='feed'),
    path(r'extractions', views.extractions, name='extractions'),
    path(r'whitelist', views.whitelist, name='whitelist'),
    path(r'indicators', views.indicators, name='indicators'),

]
