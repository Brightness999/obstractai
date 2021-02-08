from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel
from .intelgroups import IntelGroups

class Tags(BaseModel):
    name = models.CharField(max_length=100)
    isglobal = models.BooleanField(default=False)
    intelgroup = models.ForeignKey(IntelGroups, on_delete=models.CASCADE, null=True)
    
