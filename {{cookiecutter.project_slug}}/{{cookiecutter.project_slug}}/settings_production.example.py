from .settings import *
import os


DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '{{cookiecutter.project_slug}}',
        'USER': 'postgres',
        'PASSWORD': '*****',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


ALLOWED_HOSTS = [
    '{{cookiecutter.domain_name}}',
]


# Your email config goes here.
# see https://github.com/anymail/django-anymail for more details / examples

EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'

ANYMAIL = {
    "MAILGUN_API_KEY": "key-****",
    "MAILGUN_SENDER_DOMAIN": '{{cookiecutter.domain_name}}',
}

SERVER_EMAIL = 'noreply@{{cookiecutter.domain_name}}'
DEFAULT_FROM_EMAIL = '{{cookiecutter.email}}'
ADMINS = [('Your Name', '{{cookiecutter.email}}'),]

GOOGLE_ANALYTICS_ID = ''  # replace with your google analytics ID to connect to Google Analytics


STRIPE_LIVE_PUBLIC_KEY = os.environ.get("STRIPE_LIVE_PUBLIC_KEY", "<your publishable key>")
STRIPE_LIVE_SECRET_KEY = os.environ.get("STRIPE_LIVE_SECRET_KEY", "<your secret key>")
STRIPE_TEST_PUBLIC_KEY = os.environ.get("STRIPE_TEST_PUBLIC_KEY", "<your publishable key>")
STRIPE_TEST_SECRET_KEY = os.environ.get("STRIPE_TEST_SECRET_KEY", "<your secret key>")
STRIPE_LIVE_MODE = True  # Change to True in production

# Mailchimp setup

# set these values if you want to subscribe people to a mailchimp list after they sign up.
MAILCHIMP_API_KEY = ''
MAILCHIMP_LIST_ID = ''


# Sentry setup

# populate this to configure sentry. should take the form: 'https://****@sentry.io/12345'
SENTRY_DSN = ''


if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()]
    )
