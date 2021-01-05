from django.conf import settings
from django.db import models
from django.conf import settings

from apps.utils.models import BaseModel
from .intelgroups import IntelGroups


class UserIntelGroupRoles(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    intelgroup = models.ForeignKey(IntelGroups, on_delete=models.CASCADE, null=True)
    role = models.PositiveIntegerField()

    # def __str__(self):
    #     return self.role