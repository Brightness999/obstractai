from django.conf import settings
from django.db import models
from apps.utils.models import BaseModel
from .intelgroups import IntelGroups
from .globalattributes import GlobalAttributes

class GroupGlobalAttributes(BaseModel):
    intelgroup = models.ForeignKey(IntelGroups, on_delete=models.CASCADE, null=True)
    globalattribute = models.ForeignKey(GlobalAttributes, on_delete=models.CASCADE, null=True)
    isenable = models.BooleanField(default=True)
    
