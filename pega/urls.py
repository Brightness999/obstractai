"""cyobstract URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.documentation import include_docs_urls, get_schemajs_view
from rest_framework import routers
from project import views
from django.conf.urls import url
# from rest_framework_swagger.views import get_swagger_view
from project.api.swagger import get_swagger_view
# from two_factor.urls import urlpatterns as tf_urls
# from two_factor.gateways.twilio.urls import urlpatterns as tf_twilio_urls

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

schema_views = get_swagger_view(title='API')
schemajs_view = get_schemajs_view(title="API")


urlpatterns = [
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^api/docs/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # url(r'', include(tf_urls)),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('users/', include('apps.users.urls')),
    path('subscriptions/', include('apps.subscriptions.urls')),


    # path('', include('project.urls')),
    # url(r'api/docs', schema_views),
    path('app/', include('project.urls')),
    path('api/', include('project.api.urls')),
    path('', include('apps.web.urls')),
    path('pegasus/', include('pegasus.apps.examples.urls')),
    path('celery-progress/', include('celery_progress.urls')),
    # API docs
    # these are needed for schema.js
    path('docs/', include_docs_urls(title='API Docs')),
    path('schemajs/', schemajs_view, name='api_schemajs'),
    path("stripe/", include("djstripe.urls", namespace="djstripe")),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
router = routers.DefaultRouter()
urlpatterns += router.urls