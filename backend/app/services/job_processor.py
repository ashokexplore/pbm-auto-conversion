"""
Job processor for data transformation tasks
"""
from typing import Dict, Any, Optional
import asyncio
from uuid import UUID

from app.services.parsing_service import ParsingService
from app.services.ai.mapping_service import MappingService
from app.services.task_manager import task_manager, TaskStatus
from app.core.supabase import supabase_admin


class JobProcessor:
    """Processor for transformation jobs"""
    
    @staticmethod
    async def process_file_analysis(
        job_id: str,
        file_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Process file analysis job
        
        Args:
            job_id: Job ID
            file_id: File ID to analyze
            user_id: User ID
            
        Returns:
            Dict: Analysis results
        """
        try:
            # Update progress: Starting
            await task_manager.update_job_status(job_id, TaskStatus.PROCESSING, progress=10)
            
            # Parse file
            await task_manager.update_job_status(job_id, TaskStatus.PROCESSING, progress=30)
            structure = await ParsingService.analyze_structure(file_id, user_id)
            
            # Update progress: Complete
            await task_manager.update_job_status(job_id, TaskStatus.PROCESSING, progress=100)
            
            return {
                "structure": structure,
                "file_id": file_id
            }
        
        except Exception as e:
            raise Exception(f"File analysis failed: {str(e)}")
    
    @staticmethod
    async def process_mapping_generation(
        job_id: str,
        input_file_id: str,
        reference_file_id: str,
        user_id: str,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process mapping generation job
        
        Args:
            job_id: Job ID
            input_file_id: Input file ID
            reference_file_id: Reference file ID
            user_id: User ID
            provider: LLM provider
            
        Returns:
            Dict: Mapping recommendations
        """
        try:
            # Update progress: Analyzing input file
            await task_manager.update_job_status(job_id, TaskStatus.PROCESSING, progress=20)
            input_structure = await ParsingService.analyze_structure(input_file_id, user_id)
            
            # Update progress: Analyzing reference file
            await task_manager.update_job_status(job_id, TaskStatus.PROCESSING, progress=40)
            reference_structure = await ParsingService.analyze_structure(reference_file_id, user_id)
            
            # Update progress: Generating mappings
            await task_manager.update_job_status(job_id, TaskStatus.PROCESSING, progress=60)
            mapping_service = MappingService(provider=provider)
            mappings = await mapping_service.generate_mappings(
                input_structure=input_structure["structure"],
                reference_structure=reference_structure["structure"]
            )
            
            # Update progress: Complete
            await task_manager.update_job_status(job_id, TaskStatus.PROCESSING, progress=100)
            
            return {
                "input_file_id": input_file_id,
                "reference_file_id": reference_file_id,
                "mappings": mappings
            }
        
        except Exception as e:
            raise Exception(f"Mapping generation failed: {str(e)}")
    
    @staticmethod
    async def process_file_transformation(
        job_id: str,
        input_file_id: str,
        output_format: str,
        mapping_config: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Process file transformation job
        
        Args:
            job_id: Job ID
            input_file_id: Input file ID
            output_format: Desired output format
            mapping_config: Mapping configuration
            user_id: User ID
            
        Returns:
            Dict: Transformation results with output file ID
        """
        try:
            # Import here to avoid circular dependency
            from app.services.transformers.transformation_service import TransformationService
            
            # Update progress: Starting transformation
            await task_manager.update_job_status(job_id, TaskStatus.PROCESSING, progress=20)
            
            # Execute transformation
            result = await TransformationService.transform_file(
                input_file_id=input_file_id,
                mapping_config=mapping_config,
                output_format=output_format,
                user_id=user_id
            )
            
            # Update progress: Complete
            await task_manager.update_job_status(
                job_id,
                TaskStatus.PROCESSING,
                progress=100,
                result_file_id=result.get("output_file_id")
            )
            
            return {
                "input_file_id": input_file_id,
                "result_file_id": result.get("output_file_id"),
                "output_filename": result.get("output_filename"),
                "rows_processed": result.get("rows_processed"),
                "rows_transformed": result.get("rows_transformed"),
                "validation_errors": result.get("validation_errors", []),
                "error_count": result.get("error_count", 0)
            }
        
        except Exception as e:
            raise Exception(f"File transformation failed: {str(e)}")
    
    @staticmethod
    async def process_batch_files(
        job_id: str,
        file_ids: list,
        operation: str,
        user_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process multiple files in batch
        
        Args:
            job_id: Job ID
            file_ids: List of file IDs
            operation: Operation to perform
            user_id: User ID
            **kwargs: Additional arguments
            
        Returns:
            Dict: Batch processing results
        """
        try:
            total_files = len(file_ids)
            processed_files = []
            failed_files = []
            
            for idx, file_id in enumerate(file_ids):
                # Update progress
                progress = int(((idx + 1) / total_files) * 100)
                await task_manager.update_job_status(job_id, TaskStatus.PROCESSING, progress=progress)
                
                try:
                    if operation == "analyze":
                        result = await ParsingService.analyze_structure(file_id, user_id)
                        processed_files.append({"file_id": file_id, "result": result})
                    else:
                        failed_files.append({"file_id": file_id, "error": "Unknown operation"})
                
                except Exception as e:
                    failed_files.append({"file_id": file_id, "error": str(e)})
            
            return {
                "total": total_files,
                "processed": len(processed_files),
                "failed": len(failed_files),
                "results": processed_files,
                "errors": failed_files
            }
        
        except Exception as e:
            raise Exception(f"Batch processing failed: {str(e)}")

