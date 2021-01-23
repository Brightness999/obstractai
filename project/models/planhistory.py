from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel
from .intelgroups import IntelGroups
from djstripe.models import Subscription

class PlanHistory(BaseModel):
    intelgroup = models.ForeignKey(IntelGroups, on_delete=models.CASCADE, null=True)
    sub = models.ForeignKey(Subscription, on_delete=models.CASCADE, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()