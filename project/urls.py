from django.urls import path, re_path
from django.views.generic import TemplateView
from rest_framework import routers


from . import views


app_name = 'project'

urlpatterns = [
    path(r'', views.Home.as_view(), name='home'),
    path(r'<path:path>', views.Home.as_view(), name='home'),
]
