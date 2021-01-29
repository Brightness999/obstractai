import uuid

from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel
from .categories import Categories
from .intelgroups import IntelGroups

class Feeds(BaseModel):
    uniqueid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    type = models.CharField(max_length=100, null=True)
    url = models.TextField(default='')
    name = models.CharField(max_length=100)
    description = models.TextField(default='', blank=True)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    tags = models.CharField(max_length=100, blank=True)
    confidence = models.PositiveIntegerField(default=0, blank=True)
    manage_enabled = models.CharField(max_length=100, blank=True)
    intelgroup = models.ForeignKey(IntelGroups, on_delete=models.CASCADE, null=True)
    isglobal = models.BooleanField(default=False)
    time = models.PositiveIntegerField(default=60)
    # def save(self, *args, **kwargs):
        

    class Meta:
        verbose_name_plural = "Feeds"
