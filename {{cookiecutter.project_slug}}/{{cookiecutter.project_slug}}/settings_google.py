import environ

from .settings import *

env_file = os.path.join(BASE_DIR,  ".env")

SETTINGS_NAME = "{{cookiecutter.project_slug}}_settings"

if not os.path.isfile('.env'):
    import google.auth
    from google.cloud import secretmanager as sm

    _, project = google.auth.default()

    if project:
        client = sm.SecretManagerServiceClient()
        secret_path = f"projects/{project}/secrets/{SETTINGS_NAME}/versions/latest"
        payload = client.access_secret_version(request={'name': secret_path}).payload.data.decode("UTF-8")

        with open(env_file, "w") as f:
            f.write(payload)

env = environ.Env(
    DEBUG=(bool),
)
env.read_env(env_file)

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
DATABASES = {
    "default": env.db()
}

# fix ssl mixed content issues
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# update with your site/domain
ALLOWED_HOSTS = [
    '*'
]

# django storages config
INSTALLED_APPS += ["storages"] # for django-storages

# Define static storage via django-storages[google]
GS_BUCKET_NAME = env("GS_BUCKET_NAME")
DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
GS_DEFAULT_ACL = "publicRead"
