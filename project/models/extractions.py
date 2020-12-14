from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel


class Extractions(BaseModel):
    types = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    words_matched = models.CharField(max_length=100)
    user_id = models.PositiveIntegerField()
    enabled = models.CharField(max_length=100)
    
