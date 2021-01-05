from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'api'
urlpatterns = [
    path(r'test', views.home, name='home'),
    path(r'account', views.account, name='account'),
    path(r'apikeys', views.apikeys, name='apikeys'),
    path(r'webhooks', views.webhooks, name='webhooks'),
    path(r'reports', views.reports, name='reports'),
    path(r'searchreports', views.searchreports, name='searchreports'),

]
