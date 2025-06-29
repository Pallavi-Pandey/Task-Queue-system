from pydantic import BaseModel
from enum import Enum

class JobStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"

class JobCreate(BaseModel):
    name: str

class JobOut(BaseModel):
    id: int
    name: str
    status: JobStatus

    class Config:
        orm_mode = True
