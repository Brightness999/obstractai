from celery import shared_task
from celery import Celery
from celery_progress.backend import ProgressRecorder
from celery.schedules import crontab
from pega.celery import app
from project.models.intelgroups import IntelGroups

@app.task(bind=True)
def feed(self):
    IntelGroups.objects.create(name="sdf")
    return 'done'
