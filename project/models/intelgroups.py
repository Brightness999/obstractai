import uuid
import random
import string

from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel

from djstripe.models import Subscription
from .plans import Plans



class IntelGroups(BaseModel):
    uniqueid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100, default='', blank=True)
    description = models.CharField(max_length=100, default='')
    plan = models.ForeignKey(Subscription, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name is None or self.name == '':
            letters = string.digits
            self.name = 'Intel Group ' + ''. join(random.choice(letters) for i in range(10))
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "IntelGroups"

