import time
from typing import Generator

from celery import Celery
from fastapi import Depends
from sqlalchemy.orm import Session

from . import crud, models
from .database import SessionLocal, get_db as get_db_dependency

# Initialize Celery
celery_app = Celery('tasks', 
             broker='redis://localhost:6379/0', 
             backend='redis://localhost:6379/0')

# For backward compatibility
app = celery_app

# Configure Celery
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

def get_db() -> Generator[Session, None, None]:
    """Get a database session for Celery tasks"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def process_job(job_id: int, db: Session) -> str:
    """Process a job - this is the actual function that does the work"""
    try:
        # Update job status to in_progress
        job = crud.update_status(db, job_id, "in_progress")
        db.commit()
        
        # Simulate some work
        time.sleep(2)
        
        # Update job status to completed
        crud.update_status(db, job_id, "completed")
        db.commit()
        
        return f"Processed job {job_id}"
    except Exception as e:
        # Rollback any changes in case of error
        db.rollback()
        
        # Try to update status to failed
        try:
            crud.update_status(db, job_id, f"failed: {str(e)}")
            db.commit()
        except:
            db.rollback()
        
        # Re-raise the exception to mark the task as failed
        raise
    finally:
        if db:
            db.close()

# Celery task wrapper
@app.task(bind=True, name='tasks.process_job')
def process_job_task(self, job_id: int) -> str:
    """Celery task wrapper for process_job"""
    # Get a new database session for this task
    db = next(get_db())
    try:
        return process_job(job_id, db)
    finally:
        db.close()
