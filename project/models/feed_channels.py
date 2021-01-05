import uuid
from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel
from .feeds import Feeds


class FeedChannels(BaseModel):
    uniqueid = models.UUIDField(default=uuid.uuid4)
    title = models.TextField(default='', null=True)
    description = models.TextField(default='', null=True)
    link = models.TextField(default='', null=True)
    language = models.TextField(default='', null=True)
    copyright = models.TextField(default='', null=True)
    managingeditor = models.TextField(default='', null=True)
    webmaster = models.TextField(default='', null=True)
    pubdate = models.TextField(default='', null=True)
    category = models.TextField(default='', null=True)
    lastbuilddate = models.TextField(default='', null=True)
    generator = models.TextField(default='', null=True)
    docs = models.TextField(default='', null=True)
    cloud = models.TextField(default='', null=True)
    ttl = models.TextField(default='', null=True)
    image = models.TextField(default='', null=True)
    textinput = models.TextField(default='', null=True)
    skiphours = models.TextField(default='', null=True)
    skipdays = models.TextField(default='', null=True)
    feed = models.ForeignKey(Feeds, on_delete=models.CASCADE, null=True)
