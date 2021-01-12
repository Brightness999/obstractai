import uuid
from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel
from .feeds import Feeds

class FeedItems(BaseModel):
    uniqueid = models.UUIDField(default=uuid.uuid4)
    title = models.TextField(default='', null=True)
    link = models.TextField(default='', null=True)
    description = models.TextField(default='', null=True)
    author = models.TextField(default='', null=True)
    category = models.TextField(default='', null=True)
    comments = models.TextField(default='', null=True)
    enclosure = models.TextField(default='', null=True)
    pubdate = models.TextField(default='', null=True)
    guid = models.TextField(default='', null=True)
    source = models.TextField(default='', null=True)
    feed = models.ForeignKey(Feeds, on_delete=models.CASCADE, null=True)

