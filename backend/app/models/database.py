"""
Database models for the application
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


class TemplateModel(BaseModel):
    """Template model"""
    id: Optional[UUID] = None
    user_id: UUID
    name: str
    description: Optional[str] = None
    input_format: str
    output_format: str
    mapping_config: Dict[str, Any]
    transformation_rules: Optional[Dict[str, Any]] = None
    confidence_scores: Optional[Dict[str, float]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class JobModel(BaseModel):
    """Job model for batch processing"""
    id: Optional[UUID] = None
    user_id: UUID
    status: str = "pending"  # pending, processing, completed, failed
    input_file_id: Optional[UUID] = None
    reference_file_id: Optional[UUID] = None
    template_id: Optional[UUID] = None
    progress: int = Field(default=0, ge=0, le=100)
    result_file_id: Optional[UUID] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class FileMetadataModel(BaseModel):
    """File metadata model"""
    id: Optional[UUID] = None
    user_id: UUID
    filename: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    storage_path: Optional[str] = None
    structure_analysis: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

