from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel
from .globalindicators import GlobalIndicators

class Whitelists(BaseModel):
    globalindicator = models.ForeignKey(GlobalIndicators, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    value = models.CharField(max_length=100)
    enabled = models.CharField(max_length=100, null=True)
    
