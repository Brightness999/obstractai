from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel


class Plans(BaseModel):
    name = models.CharField(max_length=100)
    types = models.CharField(max_length=100)
    annual_price = models.PositiveIntegerField()
    monthly_price = models.PositiveIntegerField()
    max_feeds = models.CharField(max_length=100)
    max_users = models.PositiveIntegerField()
    enabled_custom_feeds = models.CharField(max_length=100)
    enabled_api = models.CharField(max_length=100)
    enabled_custom_extraction = models.CharField(max_length=100)
    
