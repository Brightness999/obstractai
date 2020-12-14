from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel


class Whitelists(BaseModel):
    indicator_type = models.CharField(max_length=100)
    indicator_value = models.CharField(max_length=255)
    
