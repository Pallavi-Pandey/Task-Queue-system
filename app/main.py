from fastapi import FastAPI
from app import models, database, crud, tasks
from app.database import engine
from app.schemas import JobCreate, JobOut

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/jobs/", response_model=JobOut)
def create_job(job: JobCreate):
    db_job = crud.create_job(job)
    tasks.process_job.delay(db_job.id)
    return db_job

@app.get("/jobs/{job_id}", response_model=JobOut)
def read_job(job_id: int):
    return crud.get_job(job_id)
