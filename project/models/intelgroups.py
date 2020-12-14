import uuid

from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel


class IntelGroups(BaseModel):
    uniqueid = models.UUIDField(default=uuid.uuid4)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    plan_id = models.PositiveIntegerField(null=True)

    def __str__(self):
        return self.name