from celery import Celery
import os

# Create a Celery instance
celery = Celery(
    "worker",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=['app.tasks']
)

# Configure Celery
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'app.tasks.*': {'queue': 'default'}
    },
    task_default_queue='default'
)

# Import tasks to ensure they are registered
from . import tasks  # noqa
