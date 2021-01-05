import uuid

from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel
from .categories import Categories
from .intelgroups import IntelGroups

class Feeds(BaseModel):
    uniqueid = models.UUIDField(default=uuid.uuid4)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    tags = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    manage_enabled = models.CharField(max_length=100)
    confidence = models.PositiveIntegerField(default=0)
    intelgroup = models.ForeignKey(IntelGroups, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name