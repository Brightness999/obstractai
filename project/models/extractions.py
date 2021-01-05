from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel
from .intelgroups import IntelGroups


class Extractions(BaseModel):
    types = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    words_matched = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    intelgroup = models.ForeignKey(IntelGroups, on_delete=models.CASCADE, null=True)
    enabled = models.CharField(max_length=100)
    
