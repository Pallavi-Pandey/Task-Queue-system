from app.celery_worker import celery
from app.crud import update_status
import time

@celery.task
def process_job(job_id: int):
    update_status(job_id, "running")
    time.sleep(5)
    update_status(job_id, "completed")
