from django.conf import settings
from django.db import models
from django.conf import settings

from apps.utils.models import BaseModel
from .intelgroups import IntelGroups

class APIKeys(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    groupids = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    # def __str__(self):
    #     return self.role