from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel


class UserGroupRoles(BaseModel):
    user_id = models.PositiveIntegerField()
    intelgroup_id = models.PositiveIntegerField()
    role = models.CharField(max_length=100)

    def __str__(self):
        return self.email