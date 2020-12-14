from django.urls import path

from . import views


app_name = 'subscriptions'
urlpatterns = [
    path('api/active-products/', views.ProductWithMetadataAPI.as_view(), name='products_api'),
{% if cookiecutter.use_teams == 'y' %}
    # team-specific URLs
    # todo: it would be better if these matched the /a/team-slug/subscription pattern of other pages
    path('team/<slug:team_slug>/', views.team_subscription, name='team_subscription_details'),
    path('team/<slug:team_slug>/subscription_success/',
         views.team_subscription_success, name='team_subscription_success'),
    path('team/<slug:team_slug>/demo/',
         views.team_subscription_demo, name='team_subscription_demo'),
    path('team/<slug:team_slug>/subscription-gated-page/',
         views.team_subscription_gated_page, name='team_subscription_gated_page'),
    path('team/<slug:team_slug>/stripe-portal/', views.team_create_stripe_portal_session,
         name='team_create_stripe_portal_session'),
    path('team/<slug:team_slug>/api/create_customer/',
         views.team_create_customer, name='team_create_customer'),
{% else %}
    # user-specific URLs
    path('', views.subscription, name='subscription_details'),
    path('subscription_success/', views.subscription_success, name='subscription_success'),
    path('demo/', views.subscription_demo, name='subscription_demo'),
    path('subscription-gated-page/', views.subscription_gated_page, name='subscription_gated_page'),
    path('stripe-portal/', views.create_stripe_portal_session, name='create_stripe_portal_session'),
    path('api/create_customer/', views.create_customer, name='create_customer'),
{% endif %}
]
