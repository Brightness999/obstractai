from celery import shared_task
from celery_progress.backend import ProgressRecorder
import time


@shared_task(bind=True)
def progress_bar_task(self, seconds):
    progress_recorder = ProgressRecorder(self)
    count = seconds * 10
    for i in range(count):
        time.sleep(.1)
        progress_recorder.set_progress(i + 1, count)
    return 'done'
