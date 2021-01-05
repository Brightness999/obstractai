from .settings import *

SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)
REDIS_URL = 'redis://redis:6379'  # from docker compose file
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pega',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',  # from docker compose file
        'PORT': '5432',
    }
}
