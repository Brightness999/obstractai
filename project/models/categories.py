from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel


class Categories(BaseModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Categories"
