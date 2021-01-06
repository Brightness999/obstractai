import uuid

from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel

from djstripe.models import Plan
from .plans import Plans



class IntelGroups(BaseModel):
    uniqueid = models.UUIDField(default=uuid.uuid4)
    name = models.CharField(max_length=100, default='')
    description = models.CharField(max_length=100, default='')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True)
   
