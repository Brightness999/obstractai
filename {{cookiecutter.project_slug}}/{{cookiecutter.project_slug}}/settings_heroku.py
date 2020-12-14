from .settings import *

import django_heroku
django_heroku.settings(locals())

SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)
CELERY_BROKER_URL = os.environ.get('REDIS_URL')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')

DEBUG = False
ALLOWED_HOSTS = [
    '{{ cookiecutter.domain_name }}'
]
