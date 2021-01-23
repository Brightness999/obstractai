from celery import shared_task
from celery import Celery
from celery_progress.backend import ProgressRecorder
from celery.schedules import crontab
from pega.celery import app
from project.models.intelgroups import IntelGroups


@app.task(bind=True)
def progress_bar_task(arg):
    IntelGroups.objects.create(name="sdf")
    # progress_recorder = ProgressRecorder(self)
    # count = seconds * 10
    # for i in range(count):
    #     time.sleep(.1)
    #     progress_recorder.set_progress(i + 1, count)
    return 'done'
