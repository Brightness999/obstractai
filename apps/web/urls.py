from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'web'
urlpatterns = [
    path(r'', views.home, name='home'),
    path(r'grouplist', views.grouplist, name='grouplist'),

    path(r'terms', TemplateView.as_view(template_name="web/terms.html"), name='terms'),

]
