from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel
from .feed_items import FeedItems


class IntelReports(BaseModel):
    feeditem = models.ForeignKey(FeedItems, on_delete=models.CASCADE, null=True)