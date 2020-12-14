import dj_database_url

from .settings import *

SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)
REDIS_URL = 'redis://redis:6379'  # from docker compose file
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL


DEBUG = False
DATABASES['default'] = dj_database_url.config(ssl_require=True)

# fix ssl mixed content issues
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# update with your site/domain
ALLOWED_HOSTS = [
    '*'
]

# use whitenoise for staticfiles
MIDDLEWARE += [
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
