from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel


class Users(BaseModel):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.email