"""
AI-powered mapping API endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.services.ai.mapping_service import MappingService
from app.services.parsing_service import ParsingService

router = APIRouter(prefix="/ai", tags=["AI Mapping"])


class GenerateMappingsRequest(BaseModel):
    """Request schema for generating mappings"""
    input_file_id: UUID
    reference_file_id: UUID
    provider: Optional[str] = None  # "openai" or "huggingface"


class CalculateSimilarityRequest(BaseModel):
    """Request schema for calculating similarity"""
    column1: str
    column2: str
    context: Optional[str] = ""


class GenerateTransformationRequest(BaseModel):
    """Request schema for generating transformation logic"""
    input_file_id: UUID
    reference_file_id: UUID
    input_column: str
    reference_column: str


@router.post("/generate-mappings")
async def generate_mappings(
    request: GenerateMappingsRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate AI-powered column mapping recommendations
    
    Args:
        request: Mapping generation request
        current_user: Current authenticated user
        
    Returns:
        Mapping recommendations with confidence scores
    """
    try:
        # Get file structures
        input_structure = await ParsingService.analyze_structure(
            file_id=str(request.input_file_id),
            user_id=current_user["id"]
        )
        
        reference_structure = await ParsingService.analyze_structure(
            file_id=str(request.reference_file_id),
            user_id=current_user["id"]
        )
        
        # Generate mappings
        mapping_service = MappingService(provider=request.provider)
        mappings = await mapping_service.generate_mappings(
            input_structure=input_structure["structure"],
            reference_structure=reference_structure["structure"]
        )
        
        return {
            "input_file": {
                "file_id": str(request.input_file_id),
                "filename": input_structure["filename"]
            },
            "reference_file": {
                "file_id": str(request.reference_file_id),
                "filename": reference_structure["filename"]
            },
            "mappings": mappings
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate mappings: {str(e)}"
        )


@router.post("/calculate-similarity")
async def calculate_similarity(
    request: CalculateSimilarityRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate semantic similarity between two column names
    
    Args:
        request: Similarity calculation request
        current_user: Current authenticated user
        
    Returns:
        Similarity score and reasoning
    """
    try:
        mapping_service = MappingService()
        result = await mapping_service.calculate_similarity(
            column1=request.column1,
            column2=request.column2,
            context=request.context or ""
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate similarity: {str(e)}"
        )


@router.post("/generate-transformation")
async def generate_transformation(
    request: GenerateTransformationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate transformation logic between columns
    
    Args:
        request: Transformation generation request
        current_user: Current authenticated user
        
    Returns:
        Transformation logic and steps
    """
    try:
        # Get file structures
        input_structure = await ParsingService.analyze_structure(
            file_id=str(request.input_file_id),
            user_id=current_user["id"]
        )
        
        reference_structure = await ParsingService.analyze_structure(
            file_id=str(request.reference_file_id),
            user_id=current_user["id"]
        )
        
        # Get column information
        input_col_type = input_structure["structure"]["column_types"].get(request.input_column, "string")
        input_col_samples = input_structure["structure"]["column_samples"].get(request.input_column, [])
        
        ref_col_type = reference_structure["structure"]["column_types"].get(request.reference_column, "string")
        ref_col_samples = reference_structure["structure"]["column_samples"].get(request.reference_column, [])
        
        # Generate transformation logic
        mapping_service = MappingService()
        transformation = await mapping_service.generate_transformation_logic(
            source_column=request.input_column,
            source_type=input_col_type,
            source_samples=input_col_samples,
            target_column=request.reference_column,
            target_type=ref_col_type,
            target_samples=ref_col_samples
        )
        
        return {
            "source": {
                "column": request.input_column,
                "type": input_col_type,
                "samples": input_col_samples[:3]
            },
            "target": {
                "column": request.reference_column,
                "type": ref_col_type,
                "samples": ref_col_samples[:3]
            },
            "transformation": transformation
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate transformation: {str(e)}"
        )


@router.get("/providers")
async def get_available_providers(current_user: dict = Depends(get_current_user)):
    """
    Get list of available LLM providers
    
    Returns:
        Available providers and their status
    """
    from app.services.ai.llm_provider import llm_provider
    
    return {
        "providers": {
            "openai": {
                "available": llm_provider.is_available("openai"),
                "model": "gpt-4" if llm_provider.is_available("openai") else None
            },
            "huggingface": {
                "available": llm_provider.is_available("huggingface"),
                "model": "mistralai/Mistral-7B-Instruct-v0.2" if llm_provider.is_available("huggingface") else None
            }
        },
        "default": "openai" if llm_provider.is_available("openai") else "huggingface"
    }

