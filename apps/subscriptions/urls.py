from django.urls import path

from . import views


app_name = 'subscriptions'
urlpatterns = [
    path('api/active-products/', views.ProductWithMetadataAPI.as_view(), name='products_api'),

    # user-specific URLs
    path('', views.subscription, name='subscription_details'),
    path('intelgroup/<int:groupid>', views.subscription, name='subscription_intelgroup'),
    path('subscription_success/', views.subscription_success, name='subscription_success'),
    path('demo/', views.subscription_demo, name='subscription_demo'),
    path('subscription-gated-page/', views.subscription_gated_page, name='subscription_gated_page'),
    path('stripe-portal/', views.create_stripe_portal_session, name='create_stripe_portal_session'),
    path('api/create_customer/', views.create_customer, name='create_customer'),

]
