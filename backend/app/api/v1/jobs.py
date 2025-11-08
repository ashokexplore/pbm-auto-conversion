"""
Job management endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from uuid import UUID

from app.schemas.job import (
    JobCreate,
    JobUpdate,
    JobResponse,
    JobListResponse
)
from app.core.auth import get_current_user
from app.core.supabase import supabase_admin

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new job
    
    Args:
        job_data: Job creation data
        current_user: Current authenticated user
        
    Returns:
        JobResponse: Created job
    """
    try:
        job_dict = job_data.model_dump()
        job_dict["user_id"] = current_user["id"]
        job_dict["status"] = "pending"
        job_dict["progress"] = 0
        
        response = supabase_admin.table("jobs").insert(job_dict).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create job"
            )
        
        return JobResponse(**response.data[0])
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job: {str(e)}"
        )


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    current_user: dict = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None
):
    """
    List all jobs for current user
    
    Args:
        current_user: Current authenticated user
        skip: Number of records to skip
        limit: Maximum number of records to return
        status_filter: Filter by job status
        
    Returns:
        JobListResponse: List of jobs
    """
    try:
        query = supabase_admin.table("jobs") \
            .select("*") \
            .eq("user_id", current_user["id"])
        
        if status_filter:
            query = query.eq("status", status_filter)
        
        response = query.order("created_at", desc=True) \
            .range(skip, skip + limit - 1) \
            .execute()
        
        count_query = supabase_admin.table("jobs") \
            .select("id", count="exact") \
            .eq("user_id", current_user["id"])
        
        if status_filter:
            count_query = count_query.eq("status", status_filter)
        
        count_response = count_query.execute()
        
        return JobListResponse(
            jobs=[JobResponse(**j) for j in response.data],
            total=count_response.count
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list jobs: {str(e)}"
        )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """
    Get job by ID
    
    Args:
        job_id: Job ID
        current_user: Current authenticated user
        
    Returns:
        JobResponse: Job data
    """
    try:
        response = supabase_admin.table("jobs") \
            .select("*") \
            .eq("id", str(job_id)) \
            .eq("user_id", current_user["id"]) \
            .single() \
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        return JobResponse(**response.data)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job: {str(e)}"
        )


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: UUID,
    job_data: JobUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update job status/progress
    
    Args:
        job_id: Job ID
        job_data: Job update data
        current_user: Current authenticated user
        
    Returns:
        JobResponse: Updated job
    """
    try:
        # Filter out None values
        update_dict = {k: v for k, v in job_data.model_dump().items() if v is not None}
        
        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        response = supabase_admin.table("jobs") \
            .update(update_dict) \
            .eq("id", str(job_id)) \
            .eq("user_id", current_user["id"]) \
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        return JobResponse(**response.data[0])
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update job: {str(e)}"
        )


@router.delete("/{job_id}")
async def cancel_job(
    job_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """
    Cancel/delete a job
    
    Args:
        job_id: Job ID
        current_user: Current authenticated user
    """
    try:
        # Update status to cancelled instead of deleting
        response = supabase_admin.table("jobs") \
            .update({"status": "cancelled"}) \
            .eq("id", str(job_id)) \
            .eq("user_id", current_user["id"]) \
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        return {"message": "Job cancelled successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel job: {str(e)}"
        )

