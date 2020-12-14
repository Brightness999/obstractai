from django.urls import path
from . import views


app_name = 'users'
urlpatterns = [
    path(r'profile/', views.profile, name='user_profile'),
    path(r'profile/upload-image/', views.upload_profile_image, name='upload_profile_image'),
]
