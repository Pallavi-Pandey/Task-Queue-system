from pydantic import BaseModel, Field, constr
from enum import Enum
from typing import Optional

class JobStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"

class JobCreate(BaseModel):
    name: constr(min_length=1, max_length=255) = Field(
        ...,
        description="Name of the job. Must be between 1 and 255 characters long.",
        example="Process data batch 1"
    )

class JobOut(BaseModel):
    id: int
    name: str
    status: JobStatus

    class Config:
        orm_mode = True
