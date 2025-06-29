from sqlalchemy import Column, Integer, String, Enum
from app.database import Base
import enum

class JobStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(Enum(JobStatus), default=JobStatus.pending)
