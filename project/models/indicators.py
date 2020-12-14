from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel


class Indicators(BaseModel):
    types = models.CharField(max_length=100)
    value = models.PositiveIntegerField()
    value_api = models.CharField(max_length=100)
    example = models.PositiveIntegerField()
    user_id = models.PositiveIntegerField()
    enabled = models.CharField(max_length=100)
    
