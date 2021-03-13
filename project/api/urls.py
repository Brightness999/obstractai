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
    path(r'configuredfeeds', views.configuredfeeds, name='configuredfeeds'),
    path(r'feedlist', views.feedlist, name='feedlist'),
    path(r'searchfeeds', views.searchfeeds, name='searchfeeds'),
    path(r'attributes', views.attributes, name='attributes'),
    path(r'enableglobal', views.enableglobal, name='enableglobal'),
    path(r'whitelist', views.whitelist, name='whitelist'),
    path(r'indicators', views.indicators, name='indicators'),
    path(r'invite', views.invite, name='invite'),
    # path(r'currentrole', views.currentrole, name='currentrole'),
    path(r'categories', views.categories, name='categories'),
    path(r'leavegroup', views.leavegroup, name='leavegroup'),
    path(r'deleteaccount', views.deleteaccount, name='deleteaccount'),
    path(r'intelgroups', views.intelgroups, name='intelgroups'),
    path(r'grouplist', views.grouplist, name='grouplist'),
    path(r'feedenable', views.feedenable, name='feedenable'),
    path(r'acceptinvite', views.acceptinvite, name='acceptinvite'),
    path(r'rejectinvite', views.rejectinvite, name='rejectinvite'),
    path(r'users', views.users, name='users'),
    path(r'role', views.role, name='role'),
    path(r'changegroup', views.changegroup, name='changegroup'),
    path(r'pullfeed', views.pullfeed, name='pullfeed'),
    path(r'webhook/', views.webhook, name='webhook'),
    path(r'onboarding/', views.onboarding, name='onboarding'),
    path(r'freeplan', views.freeplan, name='freeplan'),
   
]
