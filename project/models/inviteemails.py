import uuid
from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel
from .intelgroups import IntelGroups


class InviteEmails(BaseModel):
    email = models.EmailField(max_length=254)
    intelgroup = models.ForeignKey(IntelGroups, on_delete=models.CASCADE)
