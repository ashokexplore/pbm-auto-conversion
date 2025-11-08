"""
Pydantic schemas for jobs
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class JobBase(BaseModel):
    """Base job schema"""
    input_file_id: Optional[UUID] = None
    reference_file_id: Optional[UUID] = None
    template_id: Optional[UUID] = None


class JobCreate(JobBase):
    """Schema for creating a job"""
    pass


class JobUpdate(BaseModel):
    """Schema for updating a job"""
    status: Optional[str] = Field(None, pattern="^(pending|processing|completed|failed)$")
    progress: Optional[int] = Field(None, ge=0, le=100)
    result_file_id: Optional[UUID] = None
    error_message: Optional[str] = None


class JobResponse(JobBase):
    """Schema for job response"""
    id: UUID
    user_id: UUID
    status: str
    progress: int
    result_file_id: Optional[UUID] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Schema for job list response"""
    jobs: list[JobResponse]
    total: int

