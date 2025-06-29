from sqlalchemy.orm import Session
from app import models, schemas

def create_job(db: Session, job: schemas.JobCreate):
    db_job = models.Job(name=job.name)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_job(db: Session, job_id: int):
    return db.query(models.Job).filter(models.Job.id == job_id).first()

def update_status(db: Session, job_id: int, status: str):
    job = get_job(db, job_id)
    job.status = status
    db.commit()
    db.refresh(job)
    return job
