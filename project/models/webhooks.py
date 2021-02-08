import uuid
from django.conf import settings
from django.db import models
from django.conf import settings

from apps.utils.models import BaseModel
from .intelgroups import IntelGroups


class WebHooks(BaseModel):
    uniqueid = models.UUIDField(default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    intelgroup = models.ForeignKey(IntelGroups, on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=100, default='')
    endpoint = models.CharField(max_length=100, default='')
    words = models.CharField(max_length=100, default='')
    isenable = models.BooleanField(default=True)

    # def __str__(self):
    #     return self.role