import uuid

from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel
from .categories import Categories
from .intelgroups import IntelGroups
from .feeds import Feeds

class GroupFeeds(BaseModel):
    uniqueid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    feed = models.ForeignKey(Feeds, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, blank=True)
    description = models.TextField(default='', blank=True)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, null=True)
    tags = models.CharField(max_length=100, blank=True)
    confidence = models.PositiveIntegerField(default=0, blank=True)
    intelgroup = models.ForeignKey(IntelGroups, on_delete=models.CASCADE, null=True)
    isenable = models.BooleanField(default=False)
        

    class Meta:
        verbose_name_plural = "GroupFeeds"
