import pytest
from app import models, schemas, crud
from sqlalchemy.orm import Session

def test_create_job(db_session: Session):
    job_data = schemas.JobCreate(name="Test Job")
    db_job = crud.create_job(db_session, job_data)
    
    assert db_job.id is not None
    assert db_job.name == "Test Job"
    assert db_job.status == models.JobStatus.pending
    
    # Verify the job was actually saved to the database
    db_job = db_session.query(models.Job).filter(models.Job.id == db_job.id).first()
    assert db_job is not None
    assert db_job.name == "Test Job"
    assert db_job.status == models.JobStatus.pending

def test_get_job(db_session: Session):
    # Create a test job
    job = models.Job(name="Test Job", status=models.JobStatus.pending)
    db_session.add(job)
    db_session.commit()
    
    # Test getting the job
    db_job = crud.get_job(db_session, job.id)
    assert db_job is not None
    assert db_job.id == job.id
    assert db_job.name == "Test Job"
    assert db_job.status == models.JobStatus.pending

def test_get_nonexistent_job(db_session: Session):
    # Test getting a job that doesn't exist
    db_job = crud.get_job(db_session, 999999)
    assert db_job is None

def test_update_status(db_session: Session):
    # Create a test job
    job = models.Job(name="Test Job", status=models.JobStatus.pending)
    db_session.add(job)
    db_session.commit()
    
    # Update the status
    crud.update_status(db_session, job.id, "completed")
    
    # Verify the update
    updated_job = db_session.query(models.Job).filter(models.Job.id == job.id).first()
    assert updated_job.status == models.JobStatus.completed
