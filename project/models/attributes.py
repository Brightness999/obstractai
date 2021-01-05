from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel


class Atrributes(BaseModel):
    attribute = models.CharField(max_length=100)
    api_attribute = models.CharField(max_length=100)
    value_assigned = models.CharField(max_length=100)
    api_value = models.CharField(max_length=100)
    words_matched = models.CharField(max_length=100)
    user_id = models.PositiveIntegerField()
    
