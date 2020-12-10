import hashlib

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
{% set user_subscriptions_enabled = cookiecutter.use_subscriptions == 'y' and cookiecutter.use_teams != 'y' %}
{% if user_subscriptions_enabled %}from apps.subscriptions.helpers import SubscriptionModelMixin{% endif %}

class CustomUser({% if user_subscriptions_enabled %}SubscriptionModelMixin, {% endif %}AbstractUser):
    """
    Add additional fields to the user model here.
    """
    avatar = models.FileField(upload_to='profile-pictures/', null=True, blank=True)
{% if user_subscriptions_enabled %}
    subscription = models.ForeignKey('djstripe.Subscription', null=True, blank=True, on_delete=models.SET_NULL,
                                     help_text=_("The user's Stripe Subscription object, if it exists"))
{% endif %}
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