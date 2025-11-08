"""
Enhanced job management API endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.services.task_manager import task_manager
from app.services.job_processor import JobProcessor
from app.schemas.job import JobResponse

router = APIRouter(prefix="/jobs", tags=["Jobs - Enhanced"])


class CreateAnalysisJobRequest(BaseModel):
    """Request schema for file analysis job"""
    file_id: UUID


class CreateMappingJobRequest(BaseModel):
    """Request schema for mapping generation job"""
    input_file_id: UUID
    reference_file_id: UUID
    provider: Optional[str] = None


class CreateTransformationJobRequest(BaseModel):
    """Request schema for transformation job"""
    input_file_id: UUID
    output_format: str
    mapping_config: dict
    template_id: Optional[UUID] = None


class CreateBatchJobRequest(BaseModel):
    """Request schema for batch job"""
    file_ids: List[UUID]
    operation: str  # "analyze", "transform", etc.


@router.post("/analyze", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def create_analysis_job(
    request: CreateAnalysisJobRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a file analysis job
    
    Args:
        request: Analysis job request
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user
        
    Returns:
        Job ID and status
    """
    try:
        # Create job
        job_id = await task_manager.create_job(
            user_id=current_user["id"],
            job_type="analysis",
            input_file_id=str(request.file_id)
        )
        
        # Start background task
        task_manager.start_background_task(
            job_id,
            JobProcessor.process_file_analysis,
            str(request.file_id),
            current_user["id"]
        )
        
        return {
            "job_id": job_id,
            "status": "pending",
            "message": "Analysis job created and queued"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create analysis job: {str(e)}"
        )


@router.post("/mapping", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def create_mapping_job(
    request: CreateMappingJobRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a mapping generation job
    
    Args:
        request: Mapping job request
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user
        
    Returns:
        Job ID and status
    """
    try:
        # Create job
        job_id = await task_manager.create_job(
            user_id=current_user["id"],
            job_type="mapping",
            input_file_id=str(request.input_file_id),
            reference_file_id=str(request.reference_file_id)
        )
        
        # Start background task
        task_manager.start_background_task(
            job_id,
            JobProcessor.process_mapping_generation,
            str(request.input_file_id),
            str(request.reference_file_id),
            current_user["id"],
            request.provider
        )
        
        return {
            "job_id": job_id,
            "status": "pending",
            "message": "Mapping job created and queued"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create mapping job: {str(e)}"
        )


@router.post("/transform", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def create_transformation_job(
    request: CreateTransformationJobRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a file transformation job
    
    Args:
        request: Transformation job request
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user
        
    Returns:
        Job ID and status
    """
    try:
        # Create job
        job_id = await task_manager.create_job(
            user_id=current_user["id"],
            job_type="transformation",
            input_file_id=str(request.input_file_id),
            template_id=str(request.template_id) if request.template_id else None
        )
        
        # Start background task
        task_manager.start_background_task(
            job_id,
            JobProcessor.process_file_transformation,
            str(request.input_file_id),
            request.output_format,
            request.mapping_config,
            current_user["id"]
        )
        
        return {
            "job_id": job_id,
            "status": "pending",
            "message": "Transformation job created and queued"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create transformation job: {str(e)}"
        )


@router.post("/batch", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def create_batch_job(
    request: CreateBatchJobRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a batch processing job
    
    Args:
        request: Batch job request
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user
        
    Returns:
        Job ID and status
    """
    try:
        # Create job
        job_id = await task_manager.create_job(
            user_id=current_user["id"],
            job_type="batch"
        )
        
        # Start background task
        task_manager.start_background_task(
            job_id,
            JobProcessor.process_batch_files,
            [str(fid) for fid in request.file_ids],
            request.operation,
            current_user["id"]
        )
        
        return {
            "job_id": job_id,
            "status": "pending",
            "message": f"Batch job created for {len(request.file_ids)} files"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create batch job: {str(e)}"
        )


@router.get("/{job_id}/status")
async def get_job_status(
    job_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """
    Get job status and progress
    
    Args:
        job_id: Job ID
        current_user: Current authenticated user
        
    Returns:
        Job status details
    """
    try:
        job = await task_manager.get_job(str(job_id))
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Verify ownership
        if job["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this job"
            )
        
        # Check if task is still active
        active_task = task_manager.get_active_task(str(job_id))
        if active_task and not active_task.done():
            job["is_active"] = True
        else:
            job["is_active"] = False
        
        return job
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job status: {str(e)}"
        )


@router.post("/{job_id}/cancel")
async def cancel_job(
    job_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """
    Cancel a running job
    
    Args:
        job_id: Job ID
        current_user: Current authenticated user
        
    Returns:
        Cancellation status
    """
    try:
        job = await task_manager.get_job(str(job_id))
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Verify ownership
        if job["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this job"
            )
        
        # Cancel job
        cancelled = await task_manager.cancel_job(str(job_id))
        
        if cancelled:
            return {"message": "Job cancelled successfully"}
        else:
            return {"message": "Job is not running or already completed"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel job: {str(e)}"
        )

