from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel


class Plans(BaseModel):
    name = models.CharField(max_length=100)
    types = models.CharField(max_length=100)
    annual_price = models.PositiveIntegerField()
    monthly_price = models.PositiveIntegerField()
    max_feeds = models.PositiveIntegerField()
    max_users = models.PositiveIntegerField()
    enabled_custom_feeds = models.CharField(max_length=100)
    enabled_api = models.PositiveIntegerField()
    enabled_custom_extraction = models.PositiveIntegerField()
    
