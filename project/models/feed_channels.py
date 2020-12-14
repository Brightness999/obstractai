
from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel


class FeedChannels(BaseModel):
    element = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    example = models.CharField(max_length=100)
    required = models.CharField(max_length=100)
    feed_id = models.PositiveIntegerField()
