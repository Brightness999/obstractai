import uuid

from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel


class Feeds(BaseModel):
    uniqueid = models.UUIDField(default=uuid.uuid4)
    types = models.CharField(max_length=100)
    field = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    manage_enabled = models.CharField(max_length=100)

    def __str__(self):
        return self.types