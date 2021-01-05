from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel

class Tags(BaseModel):
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=100, default='custom')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
