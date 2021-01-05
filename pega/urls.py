# """pega URL Configuration

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/2.1/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
# from django.conf import settings
# from django.conf.urls.static import static
# from django.contrib import admin
# from django.urls import path, include
# from rest_framework.documentation import include_docs_urls, get_schemajs_view


# schemajs_view = get_schemajs_view(title="API")


# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('accounts/', include('allauth.urls')),
#     path('users/', include('apps.users.urls')),
#     path('subscriptions/', include('apps.subscriptions.urls')),


#     path('', include('apps.web.urls')),
#     path('pegasus/', include('pegasus.apps.examples.urls')),
#     path('celery-progress/', include('celery_progress.urls')),
#     # API docs
#     # these are needed for schema.js
#     path('docs/', include_docs_urls(title='API Docs')),
#     path('schemajs/', schemajs_view, name='api_schemajs'),

#     # djstripe urls - for webhooks
#     path("stripe/", include("djstripe.urls", namespace="djstripe")),
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

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

schemajs_view = get_schemajs_view(title="API")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('users/', include('apps.users.urls')),
    path('subscriptions/', include('apps.subscriptions.urls')),


    # path('', include('project.urls')),
    path('home/', include('project.urls')),
    path('api/', include('project.api.urls')),
    # path('home/<path:path>', include('project.urls')),
    # path('intelgroups/<path:path>', include('project.urls')),
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
router.register(r'api/intelgroups', views.RoleIntelGroupViewSet)
router.register(r'api/intelgroup', views.IntelGroupViewSet)
router.register(r'api/intelgrouprole', views.IntelGroupRoleViewSet)
router.register(r'api/users', views.UserViewSet)
router.register(r'api/user', views.UserInvitationViewSet)
router.register(r'api/customers', views.CustomerViewSet)
router.register(r'api/plans', views.PlanViewSet)
router.register(r'api/feeds', views.FeedViewSet)
router.register(r'api/categories', views.CategoryViewSet)
router.register(r'api/tags', views.TagViewSet)
router.register(r'api/extractions', views.ExtractionViewSet)
router.register(r'api/indicators', views.IndicatorViewSet)
router.register(r'api/whitelist', views.WhitelistViewSet)
router.register(r'api/apikeys', views.APIKeysViewSet)
router.register(r'api/fulltext', views.FullTextViewSet)
urlpatterns += router.urls