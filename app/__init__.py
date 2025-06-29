"""
Task Queue System - FastAPI Application
"""
from .database import Base, engine, SessionLocal, get_db
from . import models, schemas, crud, tasks

# Create database tables
Base.metadata.create_all(bind=engine)

# Export modules for easier imports
__all__ = [
    'models',
    'schemas',
    'crud',
    'tasks',
    'Base',
    'get_db',
    'engine',
    'SessionLocal'
]