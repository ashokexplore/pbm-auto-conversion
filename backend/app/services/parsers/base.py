"""
Base parser interface for all file parsers
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path


class ParseResult:
    """Standard parser result format"""
    
    def __init__(
        self,
        data: List[Dict[str, Any]],
        headers: List[str],
        metadata: Dict[str, Any],
        sample_data: Optional[List[Dict[str, Any]]] = None
    ):
        self.data = data
        self.headers = headers
        self.metadata = metadata
        self.sample_data = sample_data or data[:10]  # First 10 rows by default
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "headers": self.headers,
            "metadata": self.metadata,
            "sample_data": self.sample_data,
            "total_rows": len(self.data)
        }


class BaseParser(ABC):
    """Abstract base class for all file parsers"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.file_name = self.file_path.name
        
    @abstractmethod
    def parse(self) -> ParseResult:
        """
        Parse the file and return standardized result
        
        Returns:
            ParseResult: Parsed data with metadata
        """
        pass
    
    @abstractmethod
    def detect_structure(self) -> Dict[str, Any]:
        """
        Detect and analyze file structure
        
        Returns:
            Dict: Structure information (columns, types, etc.)
        """
        pass
    
    def get_file_info(self) -> Dict[str, Any]:
        """Get basic file information"""
        return {
            "filename": self.file_name,
            "size": self.file_path.stat().st_size,
            "path": str(self.file_path)
        }
    
    @staticmethod
    def infer_data_type(value: Any) -> str:
        """
        Infer data type from value
        
        Args:
            value: Value to check
            
        Returns:
            str: Data type name
        """
        if value is None or value == '':
            return 'null'
        
        # Try to convert to different types
        try:
            int(value)
            return 'integer'
        except (ValueError, TypeError):
            pass
        
        try:
            float(value)
            return 'float'
        except (ValueError, TypeError):
            pass
        
        # Check for boolean
        if isinstance(value, bool) or str(value).lower() in ['true', 'false', 'yes', 'no']:
            return 'boolean'
        
        # Check for date/datetime (basic check)
        value_str = str(value)
        if any(sep in value_str for sep in ['-', '/']):
            parts = value_str.replace('-', '/').split('/')
            if len(parts) >= 2 and all(p.isdigit() for p in parts):
                return 'date'
        
        return 'string'

