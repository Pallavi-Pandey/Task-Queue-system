import pytest
from unittest.mock import patch
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models, schemas

# Test the root endpoint
def test_read_root(client):
    """Test the root endpoint returns a welcome message."""
    response = client.get("/api/v1/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Welcome to the Task Queue System"}

# Test creating a job
@patch('app.tasks.process_job_task')
def test_create_job(mock_process_job, client: TestClient, db_session: Session):
    """Test creating a new job through the API."""
    # Mock the process_job_task to avoid actual Celery task execution
    mock_process_job.delay.return_value = None
    
    job_data = {"name": "Test Job"}
    response = client.post("/api/v1/jobs/", json=job_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == job_data["name"]
    assert data["status"] == "pending"
    assert "id" in data
    
    # Verify the job was created in the database
    db_job = db_session.query(models.Job).filter(models.Job.id == data["id"]).first()
    assert db_job is not None
    assert db_job.name == job_data["name"]
    assert db_job.status == "pending"
    
    # Verify the task was called with the correct job ID
    mock_process_job.delay.assert_called_once_with(data["id"])

# Test getting a job
def test_read_job(client: TestClient, db_session: Session):
    """Test retrieving an existing job."""
    # Create a test job
    job = models.Job(name="Test Job", status=models.JobStatus.pending)
    db_session.add(job)
    db_session.commit()
    
    # Now try to read it
    response = client.get(f"/api/v1/jobs/{job.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == job.id
    assert data["name"] == job.name
    assert data["status"] == job.status.value

# Test getting a non-existent job
def test_read_nonexistent_job(client: TestClient):
    """Test retrieving a non-existent job returns 404."""
    response = client.get("/api/v1/jobs/999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

# Test creating a job with invalid data
@patch('app.tasks.process_job_task')
def test_create_job_invalid_data(mock_process_job, client: TestClient):
    """Test creating a job with invalid data returns validation errors."""
    # Mock the process_job_task to avoid actual Celery task execution
    mock_process_job.delay.return_value = None
    
    # Missing required field 'name'
    response = client.post("/api/v1/jobs/", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Empty name
    response = client.post("/api/v1/jobs/", json={"name": ""})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Name too long
    long_name = "x" * 256  # 256 characters is more than our 255 limit
    response = client.post("/api/v1/jobs/", json={"name": long_name})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Verify no tasks were called for invalid data
    mock_process_job.delay.assert_not_called()
