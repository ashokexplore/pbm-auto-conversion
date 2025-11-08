"""
Pydantic schemas for templates
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class TemplateBase(BaseModel):
    """Base template schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    input_format: str
    output_format: str
    mapping_config: Dict[str, Any]
    transformation_rules: Optional[Dict[str, Any]] = None
    confidence_scores: Optional[Dict[str, float]] = None


class TemplateCreate(TemplateBase):
    """Schema for creating a template"""
    pass


class TemplateUpdate(BaseModel):
    """Schema for updating a template"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    mapping_config: Optional[Dict[str, Any]] = None
    transformation_rules: Optional[Dict[str, Any]] = None
    confidence_scores: Optional[Dict[str, float]] = None


class TemplateResponse(TemplateBase):
    """Schema for template response"""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    """Schema for template list response"""
    templates: list[TemplateResponse]
    total: int

