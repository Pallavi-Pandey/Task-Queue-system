from fastapi import APIRouter, Depends, HTTPException, FastAPI
from sqlalchemy.orm import Session

from . import crud, models, schemas, tasks
from .database import SessionLocal, get_db

# Create a router
router = APIRouter(prefix="/api/v1")

@router.get("/")
async def read_root():
    """Root endpoint with a welcome message"""
    return {"message": "Welcome to the Task Queue System"}

@router.post("/jobs/", response_model=schemas.JobOut)
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    """Create a new job"""
    db_job = crud.create_job(db, job)
    db.commit()  # Commit to ensure job is saved before processing
    
    # Process the job in the background
    tasks.process_job_task.delay(db_job.id)
    return db_job

@router.get("/jobs/{job_id}", response_model=schemas.JobOut)
def read_job(job_id: int, db: Session = Depends(get_db)):
    """Get a job by ID"""
    db_job = crud.get_job(db, job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Task Queue System",
        description="A simple task queue system with FastAPI and Celery",
        version="1.0.0"
    )
    
    # Include the router
    app.include_router(router)
    
    # Set up database dependency
    app.dependency_overrides[get_db] = get_db
    
    return app

# Create the FastAPI application
app = create_app()
