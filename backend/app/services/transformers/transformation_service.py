"""
Data transformation service
"""
from typing import Dict, Any, List, Optional
import os
import uuid
from pathlib import Path

from app.services.transformers.engine import TransformationEngine, DataValidator
from app.services.transformers.output_generators import OutputGeneratorFactory
from app.services.parsing_service import ParsingService
from app.core.config import settings
from app.core.supabase import supabase_admin


class TransformationService:
    """Service for data transformation operations"""
    
    @staticmethod
    async def transform_file(
        input_file_id: str,
        mapping_config: Dict[str, Any],
        output_format: str,
        user_id: str,
        output_filename: Optional[str] = None,
        validation_rules: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Transform a file using mapping configuration
        
        Args:
            input_file_id: Input file ID
            mapping_config: Mapping configuration
            output_format: Desired output format
            user_id: User ID
            output_filename: Optional output filename
            validation_rules: Optional validation rules
            
        Returns:
            Dict with transformation results and output file ID
        """
        # Parse input file
        parsed_result = await ParsingService.parse_file(input_file_id, user_id)
        input_data = parsed_result.get("full_data", [])
        
        if not input_data:
            raise ValueError("No data found in input file")
        
        # Create transformation engine
        engine = TransformationEngine()
        engine.add_rules_from_config(mapping_config)
        
        # Transform data
        transformed_data = engine.transform_data(input_data)
        
        # Get target headers from mapping
        target_headers = [
            mapping.get("reference_column") or mapping.get("target_column")
            for mapping in mapping_config.get("mappings", [])
            if mapping.get("reference_column") or mapping.get("target_column")
        ]
        
        if not target_headers:
            # Use all columns from first transformed row
            if transformed_data:
                target_headers = list(transformed_data[0].keys())
        
        # Generate output file
        if not output_filename:
            output_filename = f"transformed_{uuid.uuid4()}.{output_format}"
        
        output_path = os.path.join(settings.UPLOAD_DIR, output_filename)
        
        # Create output generator
        generator = OutputGeneratorFactory.create_generator(
            output_format,
            transformed_data,
            target_headers
        )
        
        # Generate output
        output_path = generator.generate(output_path)
        
        # Get file size
        file_size = os.path.getsize(output_path)
        
        # Save file metadata
        file_metadata = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "filename": output_filename,
            "file_type": output_format,
            "file_size": file_size,
            "storage_path": output_path,
        }
        
        result = supabase_admin.table("file_metadata").insert(file_metadata).execute()
        output_file_id = result.data[0]["id"] if result.data else None
        
        # Get validation errors
        validation_errors = engine.get_validation_errors()
        
        return {
            "success": True,
            "output_file_id": output_file_id,
            "output_filename": output_filename,
            "output_path": output_path,
            "rows_processed": len(input_data),
            "rows_transformed": len(transformed_data),
            "validation_errors": validation_errors,
            "error_count": len(validation_errors)
        }
    
    @staticmethod
    async def validate_transformation(
        input_file_id: str,
        mapping_config: Dict[str, Any],
        user_id: str,
        sample_size: int = 10
    ) -> Dict[str, Any]:
        """
        Validate transformation without generating output
        
        Args:
            input_file_id: Input file ID
            mapping_config: Mapping configuration
            user_id: User ID
            sample_size: Number of rows to sample for validation
            
        Returns:
            Dict with validation results
        """
        # Parse input file
        parsed_result = await ParsingService.parse_file(input_file_id, user_id)
        input_data = parsed_result.get("full_data", [])
        
        # Sample data
        sample_data = input_data[:sample_size]
        
        # Create transformation engine
        engine = TransformationEngine()
        engine.add_rules_from_config(mapping_config)
        
        # Transform sample
        transformed_sample = engine.transform_data(sample_data)
        
        # Get validation errors
        validation_errors = engine.get_validation_errors()
        
        return {
            "valid": len(validation_errors) == 0,
            "sample_size": len(sample_data),
            "transformed_count": len(transformed_sample),
            "validation_errors": validation_errors,
            "sample_input": sample_data[:3],
            "sample_output": transformed_sample[:3]
        }
    
    @staticmethod
    async def preview_transformation(
        input_file_id: str,
        mapping_config: Dict[str, Any],
        user_id: str,
        preview_rows: int = 10
    ) -> Dict[str, Any]:
        """
        Preview transformation results
        
        Args:
            input_file_id: Input file ID
            mapping_config: Mapping configuration
            user_id: User ID
            preview_rows: Number of rows to preview
            
        Returns:
            Dict with preview data
        """
        result = await TransformationService.validate_transformation(
            input_file_id,
            mapping_config,
            user_id,
            sample_size=preview_rows
        )
        
        return {
            "preview": {
                "input": result["sample_input"],
                "output": result["sample_output"]
            },
            "validation": {
                "valid": result["valid"],
                "errors": result["validation_errors"]
            }
        }
    
    @staticmethod
    def get_supported_output_formats() -> List[str]:
        """Get list of supported output formats"""
        return OutputGeneratorFactory.get_supported_formats()

