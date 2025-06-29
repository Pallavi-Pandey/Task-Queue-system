import os
import sys
from pathlib import Path
from typing import Generator, Callable

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import create_app
from app.tasks import app as celery_app

# Configure Celery to run tasks synchronously during testing
celery_app.conf.update(
    task_always_eager=True,
    task_eager_propagates=True,
    broker_url='memory://',
    result_backend='cache+memory://',
)

# Set testing environment variable
os.environ["TESTING"] = "1"

# Create a test database in memory
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create a test engine with SQLite in-memory database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create a test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the test database
Base.metadata.create_all(bind=engine)

# Fixture to provide a test database session
@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a new database session for each test with automatic rollback"""
    # Begin a non-ORM transaction
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Start a nested transaction
    nested = connection.begin_nested()

    # If the application code calls session.commit, it will end the nested
    # transaction. We need to start a new one so that tests can continue
    # to use the session.
    @event.listens_for(session, 'after_transaction_end')
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    # Cleanup
    session.close()
    transaction.rollback()
    connection.close()

# Fixture to provide a test client
@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client that uses the override_get_db fixture.
    """
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            db_session.rollback()

    # Create a new test app for each test
    test_app = create_app()
    
    # Override the database dependency
    test_app.dependency_overrides[get_db] = override_get_db
    
    # Create test client with the test app
    with TestClient(test_app) as test_client:
        yield test_client
    
    # Clear overrides after the test
    test_app.dependency_overrides.clear()
