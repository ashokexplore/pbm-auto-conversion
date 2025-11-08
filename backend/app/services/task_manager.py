"""
Background task manager for async job processing
"""
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from uuid import UUID
import asyncio
from functools import wraps

from app.core.supabase import supabase_admin


class TaskStatus:
    """Task status constants"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BackgroundTaskManager:
    """Manager for background tasks and job tracking"""
    
    def __init__(self):
        self._active_tasks: Dict[str, asyncio.Task] = {}
        
    async def create_job(
        self,
        user_id: str,
        job_type: str,
        input_file_id: Optional[str] = None,
        reference_file_id: Optional[str] = None,
        template_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new job in the database
        
        Args:
            user_id: User ID
            job_type: Type of job
            input_file_id: Input file ID
            reference_file_id: Reference file ID
            template_id: Template ID
            metadata: Additional metadata
            
        Returns:
            str: Job ID
        """
        job_data = {
            "user_id": user_id,
            "status": TaskStatus.PENDING,
            "progress": 0,
            "input_file_id": input_file_id,
            "reference_file_id": reference_file_id,
            "template_id": template_id,
        }
        
        response = supabase_admin.table("jobs").insert(job_data).execute()
        
        if not response.data:
            raise ValueError("Failed to create job")
        
        return response.data[0]["id"]
    
    async def update_job_status(
        self,
        job_id: str,
        status: str,
        progress: Optional[int] = None,
        error_message: Optional[str] = None,
        result_file_id: Optional[str] = None
    ):
        """
        Update job status and progress
        
        Args:
            job_id: Job ID
            status: New status
            progress: Progress percentage (0-100)
            error_message: Error message if failed
            result_file_id: Result file ID if completed
        """
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if progress is not None:
            update_data["progress"] = min(100, max(0, progress))
        
        if error_message:
            update_data["error_message"] = error_message
        
        if result_file_id:
            update_data["result_file_id"] = result_file_id
        
        supabase_admin.table("jobs").update(update_data).eq("id", job_id).execute()
    
    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job details"""
        response = supabase_admin.table("jobs").select("*").eq("id", job_id).single().execute()
        return response.data if response.data else None
    
    async def execute_task(
        self,
        job_id: str,
        task_func: Callable,
        *args,
        **kwargs
    ):
        """
        Execute a task with job tracking
        
        Args:
            job_id: Job ID
            task_func: Async function to execute
            *args: Task arguments
            **kwargs: Task keyword arguments
        """
        try:
            # Update status to processing
            await self.update_job_status(job_id, TaskStatus.PROCESSING, progress=0)
            
            # Execute task
            result = await task_func(job_id, *args, **kwargs)
            
            # Update status to completed
            await self.update_job_status(
                job_id,
                TaskStatus.COMPLETED,
                progress=100,
                result_file_id=result.get("result_file_id") if isinstance(result, dict) else None
            )
            
            return result
        
        except Exception as e:
            # Update status to failed
            await self.update_job_status(
                job_id,
                TaskStatus.FAILED,
                error_message=str(e)
            )
            raise
    
    def start_background_task(
        self,
        job_id: str,
        task_func: Callable,
        *args,
        **kwargs
    ) -> asyncio.Task:
        """
        Start a background task
        
        Args:
            job_id: Job ID
            task_func: Async function to execute
            *args: Task arguments
            **kwargs: Task keyword arguments
            
        Returns:
            asyncio.Task: Task object
        """
        task = asyncio.create_task(
            self.execute_task(job_id, task_func, *args, **kwargs)
        )
        
        self._active_tasks[job_id] = task
        
        # Clean up when done
        task.add_done_callback(lambda t: self._active_tasks.pop(job_id, None))
        
        return task
    
    async def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a running job
        
        Args:
            job_id: Job ID
            
        Returns:
            bool: True if cancelled, False if not found
        """
        task = self._active_tasks.get(job_id)
        
        if task and not task.done():
            task.cancel()
            await self.update_job_status(job_id, TaskStatus.CANCELLED)
            return True
        
        return False
    
    def get_active_task(self, job_id: str) -> Optional[asyncio.Task]:
        """Get active task by job ID"""
        return self._active_tasks.get(job_id)


# Global task manager instance
task_manager = BackgroundTaskManager()


def track_progress(job_id: str):
    """
    Decorator to track progress of a task
    
    Usage:
        @track_progress(job_id)
        async def my_task(job_id, ...):
            # Task code
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                await task_manager.update_job_status(
                    job_id,
                    TaskStatus.FAILED,
                    error_message=str(e)
                )
                raise
        return wrapper
    return decorator

