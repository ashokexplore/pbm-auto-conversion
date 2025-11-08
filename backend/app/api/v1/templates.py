"""
Template management endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional
from uuid import UUID

from app.schemas.template import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    TemplateListResponse
)
from app.core.auth import get_current_user
from app.core.supabase import supabase_admin

router = APIRouter(prefix="/templates", tags=["Templates"])


@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new template
    
    Args:
        template_data: Template creation data
        current_user: Current authenticated user
        
    Returns:
        TemplateResponse: Created template
    """
    try:
        template_dict = template_data.model_dump()
        template_dict["user_id"] = current_user["id"]
        
        response = supabase_admin.table("templates").insert(template_dict).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create template"
            )
        
        return TemplateResponse(**response.data[0])
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create template: {str(e)}"
        )


@router.get("/", response_model=TemplateListResponse)
async def list_templates(
    current_user: dict = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """
    List all templates for current user
    
    Args:
        current_user: Current authenticated user
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        TemplateListResponse: List of templates
    """
    try:
        response = supabase_admin.table("templates") \
            .select("*") \
            .eq("user_id", current_user["id"]) \
            .order("created_at", desc=True) \
            .range(skip, skip + limit - 1) \
            .execute()
        
        count_response = supabase_admin.table("templates") \
            .select("id", count="exact") \
            .eq("user_id", current_user["id"]) \
            .execute()
        
        return TemplateListResponse(
            templates=[TemplateResponse(**t) for t in response.data],
            total=count_response.count
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list templates: {str(e)}"
        )


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """
    Get template by ID
    
    Args:
        template_id: Template ID
        current_user: Current authenticated user
        
    Returns:
        TemplateResponse: Template data
    """
    try:
        response = supabase_admin.table("templates") \
            .select("*") \
            .eq("id", str(template_id)) \
            .eq("user_id", current_user["id"]) \
            .single() \
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        return TemplateResponse(**response.data)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template: {str(e)}"
        )


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: UUID,
    template_data: TemplateUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update template
    
    Args:
        template_id: Template ID
        template_data: Template update data
        current_user: Current authenticated user
        
    Returns:
        TemplateResponse: Updated template
    """
    try:
        # Filter out None values
        update_dict = {k: v for k, v in template_data.model_dump().items() if v is not None}
        
        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        response = supabase_admin.table("templates") \
            .update(update_dict) \
            .eq("id", str(template_id)) \
            .eq("user_id", current_user["id"]) \
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        return TemplateResponse(**response.data[0])
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update template: {str(e)}"
        )


@router.delete("/{template_id}")
async def delete_template(
    template_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete template
    
    Args:
        template_id: Template ID
        current_user: Current authenticated user
    """
    try:
        response = supabase_admin.table("templates") \
            .delete() \
            .eq("id", str(template_id)) \
            .eq("user_id", current_user["id"]) \
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        return {"message": "Template deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete template: {str(e)}"
        )

