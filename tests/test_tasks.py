import pytest
from unittest.mock import patch, MagicMock, ANY
from sqlalchemy.orm import Session

from app import tasks, models, crud
from app.database import SessionLocal

# Test the process_job function
def test_process_job_success(db_session: Session):
    # Create a test job
    job = models.Job(id=1, name="Test Job", status=models.JobStatus.pending)
    
    # Create a mock session
    mock_session = MagicMock()
    
    # Set up the mock to return our test job
    mock_job = MagicMock()
    mock_job.id = job.id
    mock_session.query.return_value.filter.return_value.first.return_value = mock_job
    
    # Mock the update_status method
    def mock_update_status(db, job_id, status):
        mock_job.status = status
        return mock_job
    
    with patch('app.crud.update_status', side_effect=mock_update_status):
        # Call the function directly with the mock session
        result = tasks.process_job(job.id, mock_session)
        
        # Verify the task completed successfully
        assert result == f"Processed job {job.id}"
        
        # Verify the session was used to update the status
        assert mock_session.commit.call_count == 2  # Once for in_progress, once for completed
        
        # Verify the job status was updated to completed
        assert mock_job.status == "completed"

# Test task failure
def test_process_job_failure():
    # Create a test job ID
    job_id = 1
    
    # Create a mock session
    mock_session = MagicMock()
    
    # Set up the mock to return our test job
    mock_job = MagicMock()
    mock_job.id = job_id
    mock_session.query.return_value.filter.return_value.first.return_value = mock_job
    
    # Mock the update_status method to raise an exception on the second call
    def mock_update_status(db, job_id, status):
        if status == "completed":
            raise Exception("Test error")
        mock_job.status = status
        return mock_job
    
    # Track rollback calls
    rollback_called = False
    def mock_rollback():
        nonlocal rollback_called
        rollback_called = True
    
    mock_session.rollback = mock_rollback
    
    with patch('app.crud.update_status', side_effect=mock_update_status):
        # Call the function and verify it raises an exception
        with pytest.raises(Exception) as exc_info:
            tasks.process_job(job_id, mock_session)
        
        # Verify the exception was raised
        assert "Test error" in str(exc_info.value)
        
        # Verify rollback was called
        assert rollback_called, "rollback() was not called"

# Test the Celery task wrapper
@patch('app.tasks.process_job')
@patch('app.tasks.get_db')
def test_process_job_task(mock_get_db, mock_process_job, db_session: Session):
    # Setup test data
    job_id = 1
    expected_result = f"Processed job {job_id}"
    
    # Setup mocks
    mock_db = MagicMock()
    mock_get_db.return_value = iter([mock_db])
    mock_process_job.return_value = expected_result
    
    # Call the Celery task
    result = tasks.process_job_task(job_id)
    
    # Verify the result
    assert result == expected_result
    
    # Verify the database session was used
    mock_get_db.assert_called_once()
    mock_process_job.assert_called_once_with(job_id, mock_db)
    mock_db.close.assert_called_once()
