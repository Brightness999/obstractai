from django.conf import settings
from django.db import models
from apps.utils.models import BaseModel
from .intelgroups import IntelGroups

class GlobalAttributes(BaseModel):
    attribute = models.CharField(max_length=100, default='')
    api_attribute = models.CharField(max_length=100, default='')
    value = models.CharField(max_length=100, default='')
    api_value = models.CharField(max_length=100, default='')
    words_matched = models.CharField(max_length=100, default='')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    intelgroup = models.ForeignKey(IntelGroups, on_delete=models.CASCADE)
    enabled = models.CharField(max_length=100, default='Enable')
    
