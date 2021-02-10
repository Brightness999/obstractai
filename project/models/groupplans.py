from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel

from djstripe.models import Subscription

class GroupPlan(BaseModel):
    name = models.CharField(default="", max_length=100)
    description = models.CharField(default="", max_length=300)
    active = models.BooleanField(default=True)
    annual_amount = models.PositiveIntegerField(default=0)
    monthly_amount = models.PositiveIntegerField(default=0)
    max_users = models.PositiveIntegerField(default=0)
    max_feeds = models.PositiveIntegerField(default=0)
    custom_feeds = models.BooleanField(default=False)
    custom_observables = models.BooleanField(default=False)
    api_access = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "GroupPlan"