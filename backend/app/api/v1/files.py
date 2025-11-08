"""
File upload and management endpoints
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List, Optional
import os
import uuid
from pathlib import Path
import shutil

from app.schemas.file import (
    FileUploadResponse,
    FileMetadataResponse,
    FileListResponse,
    FileStructureResponse
)
from app.core.auth import get_current_user
from app.core.config import settings
from app.core.supabase import supabase_admin

router = APIRouter(prefix="/files", tags=["Files"])

# Ensure upload directories exist
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.TEMP_DIR).mkdir(parents=True, exist_ok=True)


def validate_file_size(file: UploadFile) -> bool:
    """
    Validate file size
    
    Args:
        file: Uploaded file
        
    Returns:
        bool: True if valid, raises exception otherwise
    """
    # Get file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
        )
    
    return True


def detect_file_type(filename: str) -> str:
    """
    Detect file type from filename
    
    Args:
        filename: Name of the file
        
    Returns:
        str: File type
    """
    extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'unknown'
    
    file_type_map = {
        'csv': 'csv',
        'txt': 'text',
        'xls': 'excel',
        'xlsx': 'excel',
        'json': 'json',
        'xml': 'xml',
        'tsv': 'tsv',
        'pdf': 'pdf',
        'docx': 'docx',
        'jpg': 'image',
        'jpeg': 'image',
        'png': 'image',
    }
    
    return file_type_map.get(extension, 'unknown')


async def save_file_chunk(file: UploadFile, file_path: str, chunk_size: int = 1024 * 1024):
    """
    Save file in chunks to handle large files
    
    Args:
        file: Uploaded file
        file_path: Path to save file
        chunk_size: Size of each chunk in bytes (default 1MB)
    """
    with open(file_path, 'wb') as buffer:
        while chunk := await file.read(chunk_size):
            buffer.write(chunk)


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    background_tasks: BackgroundTasks = None
):
    """
    Upload a file for processing
    
    Args:
        file: File to upload
        current_user: Current authenticated user
        background_tasks: Background tasks
        
    Returns:
        FileUploadResponse: Upload confirmation with file metadata
    """
    # Validate file size
    validate_file_size(file)
    
    # Generate unique file ID and path
    file_id = uuid.uuid4()
    file_extension = file.filename.rsplit('.', 1)[-1] if '.' in file.filename else ''
    safe_filename = f"{file_id}.{file_extension}" if file_extension else str(file_id)
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
    
    # Detect file type
    file_type = detect_file_type(file.filename)
    
    try:
        # Save file in chunks
        await save_file_chunk(file, file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Save file metadata to database
        metadata = {
            "id": str(file_id),
            "user_id": current_user["id"],
            "filename": file.filename,
            "file_type": file_type,
            "file_size": file_size,
            "storage_path": file_path,
        }
        
        result = supabase_admin.table("file_metadata").insert(metadata).execute()
        
        return FileUploadResponse(
            file_id=file_id,
            filename=file.filename,
            file_type=file_type,
            file_size=file_size,
            message="File uploaded successfully"
        )
    
    except Exception as e:
        # Clean up file if database operation fails
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )


@router.get("/", response_model=FileListResponse)
async def list_files(
    current_user: dict = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """
    List all files for current user
    
    Args:
        current_user: Current authenticated user
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        FileListResponse: List of files
    """
    try:
        # Query files from database
        response = supabase_admin.table("file_metadata") \
            .select("*") \
            .eq("user_id", current_user["id"]) \
            .order("created_at", desc=True) \
            .range(skip, skip + limit - 1) \
            .execute()
        
        # Get total count
        count_response = supabase_admin.table("file_metadata") \
            .select("id", count="exact") \
            .eq("user_id", current_user["id"]) \
            .execute()
        
        return FileListResponse(
            files=[FileMetadataResponse(**file) for file in response.data],
            total=count_response.count
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}"
        )


@router.get("/{file_id}", response_model=FileMetadataResponse)
async def get_file_metadata(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get file metadata
    
    Args:
        file_id: File ID
        current_user: Current authenticated user
        
    Returns:
        FileMetadataResponse: File metadata
    """
    try:
        response = supabase_admin.table("file_metadata") \
            .select("*") \
            .eq("id", file_id) \
            .eq("user_id", current_user["id"]) \
            .single() \
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        return FileMetadataResponse(**response.data)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file metadata: {str(e)}"
        )


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a file
    
    Args:
        file_id: File ID
        current_user: Current authenticated user
    """
    try:
        # Get file metadata
        response = supabase_admin.table("file_metadata") \
            .select("*") \
            .eq("id", file_id) \
            .eq("user_id", current_user["id"]) \
            .single() \
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        file_data = response.data
        
        # Delete file from storage
        if file_data.get("storage_path") and os.path.exists(file_data["storage_path"]):
            os.remove(file_data["storage_path"])
        
        # Delete metadata from database
        supabase_admin.table("file_metadata") \
            .delete() \
            .eq("id", file_id) \
            .eq("user_id", current_user["id"]) \
            .execute()
        
        return {"message": "File deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )


@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Download a file
    
    Args:
        file_id: File ID
        current_user: Current authenticated user
        
    Returns:
        FileResponse: File download
    """
    try:
        # Get file metadata
        response = supabase_admin.table("file_metadata") \
            .select("*") \
            .eq("id", file_id) \
            .eq("user_id", current_user["id"]) \
            .single() \
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        file_data = response.data
        file_path = file_data.get("storage_path")
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on storage"
            )
        
        return FileResponse(
            path=file_path,
            filename=file_data["filename"],
            media_type="application/octet-stream"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download file: {str(e)}"
        )

