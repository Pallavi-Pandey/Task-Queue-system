from celery import Celery
import os

celery = Celery(
    "worker",
    broker=os.getenv("REDIS_URL", "redis://redis:6379"),
)

celery.conf.task_routes = {"app.tasks.*": {"queue": "default"}}
