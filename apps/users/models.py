import hashlib

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.subscriptions.helpers import SubscriptionModelMixin

class CustomUser(SubscriptionModelMixin, AbstractUser):
    """
    Add additional fields to the user model here.
    """
    avatar = models.FileField(upload_to='profile-pictures/', null=True, blank=True)

    subscription = models.ForeignKey('djstripe.Subscription', null=True, blank=True, on_delete=models.SET_NULL,
                                     help_text=_("The user's Stripe Subscription object, if it exists"))
    
    onboarding = models.BooleanField(default=True)
    is_mailerlite = models.BooleanField(default=False)

    def __str__(self):
        return self.email

    def get_display_name(self):
        if self.get_full_name().strip():
            return self.get_full_name()
        return self.email

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        else:
            return 'https://www.gravatar.com/avatar/{}?s=128&d=identicon'.format(self.gravatar_id)

    @property
    def gravatar_id(self):
        # https://en.gravatar.com/site/implement/hash/
        return hashlib.md5(self.email.lower().strip().encode('utf-8')).hexdigest()
