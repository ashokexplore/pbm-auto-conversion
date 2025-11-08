"""
File parsing API endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional
from uuid import UUID

from app.core.auth import get_current_user
from app.services.parsing_service import ParsingService
from app.schemas.file import FileStructureResponse
from pydantic import BaseModel

router = APIRouter(prefix="/parse", tags=["Parsing"])


class ParseFileRequest(BaseModel):
    """Request schema for parsing a file"""
    file_id: UUID
    file_type: Optional[str] = None


class AnalyzeStructureRequest(BaseModel):
    """Request schema for structure analysis"""
    file_id: UUID
    file_type: Optional[str] = None


class CompareStructuresRequest(BaseModel):
    """Request schema for comparing file structures"""
    input_file_id: UUID
    reference_file_id: UUID


@router.post("/file")
async def parse_file(
    request: ParseFileRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Parse a file and return structured data
    
    Args:
        request: Parse request
        current_user: Current authenticated user
        
    Returns:
        Parsed data with metadata
    """
    try:
        result = await ParsingService.parse_file(
            file_id=str(request.file_id),
            user_id=current_user["id"],
            file_type=request.file_type
        )
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse file: {str(e)}"
        )


@router.post("/analyze")
async def analyze_structure(
    request: AnalyzeStructureRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze file structure without loading all data
    
    Args:
        request: Analyze request
        current_user: Current authenticated user
        
    Returns:
        Structure analysis
    """
    try:
        result = await ParsingService.analyze_structure(
            file_id=str(request.file_id),
            user_id=current_user["id"],
            file_type=request.file_type
        )
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze file: {str(e)}"
        )


@router.post("/compare")
async def compare_structures(
    request: CompareStructuresRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Compare structures of two files for mapping
    
    Args:
        request: Compare request
        current_user: Current authenticated user
        
    Returns:
        Structure comparison with potential mappings
    """
    try:
        result = await ParsingService.compare_structures(
            input_file_id=str(request.input_file_id),
            reference_file_id=str(request.reference_file_id),
            user_id=current_user["id"]
        )
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare files: {str(e)}"
        )


@router.get("/supported-types")
async def get_supported_types():
    """
    Get list of supported file types
    
    Returns:
        List of supported file types
    """
    from app.services.parsers.factory import ParserFactory
    
    return {
        "supported_types": ParserFactory.get_supported_types(),
        "type_descriptions": {
            "csv": "Comma-separated values",
            "xls": "Excel 97-2003",
            "xlsx": "Excel 2007+",
            "txt": "Text file",
            "tsv": "Tab-separated values",
            "dat": "Flat/Fixed-width file",
            "fixed": "Fixed-width file"
        }
    }

