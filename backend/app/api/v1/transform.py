"""
Transformation API endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.services.transformers.transformation_service import TransformationService

router = APIRouter(prefix="/transform", tags=["Transformation"])


class TransformFileRequest(BaseModel):
    """Request schema for file transformation"""
    input_file_id: UUID
    mapping_config: dict
    output_format: str
    output_filename: Optional[str] = None


class ValidateTransformationRequest(BaseModel):
    """Request schema for validation"""
    input_file_id: UUID
    mapping_config: dict
    sample_size: Optional[int] = 10


class PreviewTransformationRequest(BaseModel):
    """Request schema for preview"""
    input_file_id: UUID
    mapping_config: dict
    preview_rows: Optional[int] = 10


@router.post("/execute")
async def execute_transformation(
    request: TransformFileRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Execute file transformation
    
    Args:
        request: Transformation request
        current_user: Current authenticated user
        
    Returns:
        Transformation results with output file ID
    """
    try:
        result = await TransformationService.transform_file(
            input_file_id=str(request.input_file_id),
            mapping_config=request.mapping_config,
            output_format=request.output_format,
            user_id=current_user["id"],
            output_filename=request.output_filename
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transformation failed: {str(e)}"
        )


@router.post("/validate")
async def validate_transformation(
    request: ValidateTransformationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Validate transformation without generating output
    
    Args:
        request: Validation request
        current_user: Current authenticated user
        
    Returns:
        Validation results
    """
    try:
        result = await TransformationService.validate_transformation(
            input_file_id=str(request.input_file_id),
            mapping_config=request.mapping_config,
            user_id=current_user["id"],
            sample_size=request.sample_size or 10
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


@router.post("/preview")
async def preview_transformation(
    request: PreviewTransformationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Preview transformation results
    
    Args:
        request: Preview request
        current_user: Current authenticated user
        
    Returns:
        Preview of input and output data
    """
    try:
        result = await TransformationService.preview_transformation(
            input_file_id=str(request.input_file_id),
            mapping_config=request.mapping_config,
            user_id=current_user["id"],
            preview_rows=request.preview_rows or 10
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preview failed: {str(e)}"
        )


@router.get("/formats")
async def get_supported_formats(current_user: dict = Depends(get_current_user)):
    """
    Get list of supported output formats
    
    Returns:
        List of supported formats
    """
    formats = TransformationService.get_supported_output_formats()
    
    return {
        "formats": formats,
        "descriptions": {
            "csv": "Comma-separated values",
            "excel": "Excel spreadsheet (.xlsx)",
            "xlsx": "Excel 2007+ format",
            "xls": "Excel 97-2003 format",
            "json": "JavaScript Object Notation",
            "tsv": "Tab-separated values",
            "pipe": "Pipe-delimited file",
            "fixed": "Fixed-width/flat file",
            "txt": "Plain text (CSV format)"
        }
    }

