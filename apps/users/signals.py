from allauth.account.signals import user_signed_up, email_confirmed
from django.conf import settings
from django.core.mail import mail_admins
from django.dispatch import receiver
from mailerlite import MailerLiteApi


@receiver(user_signed_up)
def handle_sign_up(request, user, **kwargs):
    # customize this function to do custom logic on sign up, e.g. send a welcome email
    # or subscribe them to your mailing list.
    # This example notifies the admins, in case you want to keep track of sign ups
    _notify_admins_of_signup(user)
    # and subscribes them to a mailchimp mailing list
    _subscribe_to_mailing_list(user)

    # add maillist
    mailerAPI = MailerLiteApi(settings.MAILERLIST_API_KEY)
    data = [{
        'email': user.email,
        'name': user.username
    }]
    try:
        mailerAPI.groups.add_subscribers(group_id=settings.MAILERLIST_GROUP_ID, subscribers_data=data)
    except:
        pass


@receiver(email_confirmed)
def update_user_email(sender, request, email_address, **kwargs):
    """
    When an email address is confirmed make it the primary email.
    """
    # This also sets user.email to the new email address.
    # hat tip: https://stackoverflow.com/a/29661871/8207
    email_address.set_as_primary()


def _notify_admins_of_signup(user):
    mail_admins(
        "Yowsers, someone signed up for the site!",
        "Email: {}".format(user.email)
    )


def _subscribe_to_mailing_list(user):
    # todo: better handle all of this or remove it
    try:
        from mailchimp3 import MailChimp
        from mailchimp3.mailchimpclient import MailChimpError
    except ImportError:
        return
    if getattr(settings, 'MAILCHIMP_API_KEY', None) and getattr(settings, 'MAILCHIMP_LIST_ID', None):
        client = MailChimp(mc_api=settings.MAILCHIMP_API_KEY)
        try:
            client.lists.members.create(settings.MAILCHIMP_LIST_ID, {
                'email_address': user.email,
                'status': 'subscribed',
            })
        except MailChimpError as e:
            # likely it's just that they were already subscribed so don't worry about it
            try:
                # but do log to sentry if available
                from sentry_sdk import capture_exception
                capture_exception(e)
            except ImportError:
                pass
