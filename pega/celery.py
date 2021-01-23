import os
from celery import Celery, shared_task
from celery.schedules import crontab
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pega.settings')

app = Celery('pega')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'feed': {
        'task': 'project.tasks.feed',
        'schedule': 1.0,
    }
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

