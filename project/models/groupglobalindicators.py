from django.conf import settings
from django.db import models
from apps.utils.models import BaseModel
from .intelgroups import IntelGroups
from .globalindicators import GlobalIndicators

class GroupGlobalIndicators(BaseModel):
    intelgroup = models.ForeignKey(IntelGroups, on_delete=models.CASCADE, null=True)
    globalindicator = models.ForeignKey(GlobalIndicators, on_delete=models.CASCADE, null=True)
    isenable = models.BooleanField(default=True)
    
