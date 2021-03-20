from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel
from .feed_items import FeedItems
from .globalindicators import GlobalIndicators

class Indicators(BaseModel):
    globalindicator = models.ForeignKey(GlobalIndicators, on_delete=models.CASCADE, null=True)
    value = models.TextField(default='')
    feeditem = models.ForeignKey(FeedItems, on_delete=models.CASCADE, null=True)
    
