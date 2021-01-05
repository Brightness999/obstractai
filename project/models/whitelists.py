from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel
from .indicators import Indicators

class Whitelists(BaseModel):
    indicator = models.ForeignKey(Indicators, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    value = models.CharField(max_length=100)
    enabled = models.CharField(max_length=100, null=True)
    
