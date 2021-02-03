import uuid
from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel
from .feed_items import FeedItems
from .intelgroups import IntelGroups
from .groupfeeds import GroupFeeds


class IntelReports(BaseModel):
    uniqueid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    feeditem = models.ForeignKey(FeedItems, on_delete=models.CASCADE, null=True)
    intelgroup = models.ForeignKey(IntelGroups, on_delete=models.CASCADE, null=True)
    groupfeed = models.ForeignKey(GroupFeeds, on_delete=models.CASCADE, null=True)