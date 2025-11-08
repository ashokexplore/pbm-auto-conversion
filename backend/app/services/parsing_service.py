"""
File parsing service
"""
from typing import Dict, Any, Optional
from uuid import UUID

from app.services.parsers.factory import ParserFactory
from app.core.supabase import supabase_admin


class ParsingService:
    """Service for parsing files and analyzing structure"""
    
    @staticmethod
    async def parse_file(
        file_id: str,
        user_id: str,
        file_type: Optional[str] = None,
        parser_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Parse a file and return structured data
        
        Args:
            file_id: File ID
            user_id: User ID
            file_type: Optional file type override
            parser_options: Optional parser-specific options
            
        Returns:
            Dict: Parsed data and metadata
        """
        # Get file metadata from database
        response = supabase_admin.table("file_metadata") \
            .select("*") \
            .eq("id", file_id) \
            .eq("user_id", user_id) \
            .single() \
            .execute()
        
        if not response.data:
            raise ValueError("File not found")
        
        file_data = response.data
        file_path = file_data.get("storage_path")
        
        if not file_path:
            raise ValueError("File path not found")
        
        # Create parser
        parser = ParserFactory.create_parser(file_path, file_type)
        
        # Parse file
        result = parser.parse()
        
        # Convert to dict
        parsed_data = result.to_dict()
        
        return {
            "file_id": file_id,
            "filename": file_data["filename"],
            "parsed_data": parsed_data,
            "full_data": result.data  # Include full data for processing
        }
    
    @staticmethod
    async def analyze_structure(
        file_id: str,
        user_id: str,
        file_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze file structure without loading all data
        
        Args:
            file_id: File ID
            user_id: User ID
            file_type: Optional file type override
            
        Returns:
            Dict: Structure analysis
        """
        # Get file metadata
        response = supabase_admin.table("file_metadata") \
            .select("*") \
            .eq("id", file_id) \
            .eq("user_id", user_id) \
            .single() \
            .execute()
        
        if not response.data:
            raise ValueError("File not found")
        
        file_data = response.data
        file_path = file_data.get("storage_path")
        
        if not file_path:
            raise ValueError("File path not found")
        
        # Create parser
        parser = ParserFactory.create_parser(file_path, file_type)
        
        # Detect structure
        structure = parser.detect_structure()
        
        # Update file metadata with structure analysis
        supabase_admin.table("file_metadata") \
            .update({"structure_analysis": structure}) \
            .eq("id", file_id) \
            .execute()
        
        return {
            "file_id": file_id,
            "filename": file_data["filename"],
            "structure": structure
        }
    
    @staticmethod
    async def compare_structures(
        input_file_id: str,
        reference_file_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Compare structures of two files for mapping
        
        Args:
            input_file_id: Input file ID
            reference_file_id: Reference file ID
            user_id: User ID
            
        Returns:
            Dict: Structure comparison
        """
        # Analyze both files
        input_structure = await ParsingService.analyze_structure(
            input_file_id, user_id
        )
        reference_structure = await ParsingService.analyze_structure(
            reference_file_id, user_id
        )
        
        # Compare columns
        input_columns = set(input_structure["structure"].get("columns", []))
        reference_columns = set(reference_structure["structure"].get("columns", []))
        
        # Find matches (exact and similar)
        exact_matches = input_columns & reference_columns
        input_only = input_columns - reference_columns
        reference_only = reference_columns - reference_columns
        
        return {
            "input_file": {
                "file_id": input_file_id,
                "filename": input_structure["filename"],
                "structure": input_structure["structure"]
            },
            "reference_file": {
                "file_id": reference_file_id,
                "filename": reference_structure["filename"],
                "structure": reference_structure["structure"]
            },
            "comparison": {
                "exact_matches": list(exact_matches),
                "input_only_columns": list(input_only),
                "reference_only_columns": list(reference_only),
                "match_percentage": len(exact_matches) / max(len(input_columns), 1) * 100
            }
        }

