"""
Pydantic schemas for file operations
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class FileUploadResponse(BaseModel):
    """Schema for file upload response"""
    file_id: UUID
    filename: str
    file_type: str
    file_size: int
    message: str


class FileMetadataResponse(BaseModel):
    """Schema for file metadata response"""
    id: UUID
    user_id: UUID
    filename: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    storage_path: Optional[str] = None
    structure_analysis: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FileStructureResponse(BaseModel):
    """Schema for file structure analysis response"""
    file_id: UUID
    filename: str
    file_type: str
    structure: Dict[str, Any]
    sample_data: Optional[list] = None
    metadata: Dict[str, Any]


class FileListResponse(BaseModel):
    """Schema for file list response"""
    files: list[FileMetadataResponse]
    total: int

