from app import models, database
from app.schemas import JobCreate

db = database.SessionLocal()

def create_job(job: JobCreate):
    db_job = models.Job(name=job.name)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_job(job_id: int):
    return db.query(models.Job).filter(models.Job.id == job_id).first()

def update_status(job_id: int, status: str):
    job = get_job(job_id)
    job.status = status
    db.commit()
    db.refresh(job)
