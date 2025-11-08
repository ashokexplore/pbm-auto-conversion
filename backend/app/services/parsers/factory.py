"""
Parser factory for creating appropriate parser instances
"""
from typing import Optional
from pathlib import Path

from app.services.parsers.base import BaseParser
from app.services.parsers.csv_parser import CSVParser
from app.services.parsers.excel_parser import ExcelParser
from app.services.parsers.txt_parser import TXTParser
from app.services.parsers.pipe_parser import PipeDelimitedParser
from app.services.parsers.flat_file_parser import FlatFileParser


class ParserFactory:
    """Factory for creating file parsers based on file type"""
    
    # Map file extensions to parser classes
    PARSER_MAP = {
        'csv': CSVParser,
        'xls': ExcelParser,
        'xlsx': ExcelParser,
        'txt': TXTParser,
        'tsv': PipeDelimitedParser,  # TSV is a type of pipe-delimited
        'dat': FlatFileParser,
        'fixed': FlatFileParser,
    }
    
    @classmethod
    def create_parser(cls, file_path: str, file_type: Optional[str] = None) -> BaseParser:
        """
        Create appropriate parser for the file
        
        Args:
            file_path: Path to the file
            file_type: Optional file type override
            
        Returns:
            BaseParser: Parser instance
            
        Raises:
            ValueError: If file type is not supported
        """
        path = Path(file_path)
        
        # Determine file type
        if file_type:
            extension = file_type.lower()
        else:
            extension = path.suffix.lstrip('.').lower()
        
        # Get parser class
        parser_class = cls.PARSER_MAP.get(extension)
        
        if not parser_class:
            raise ValueError(f"Unsupported file type: {extension}")
        
        return parser_class(file_path)
    
    @classmethod
    def get_supported_types(cls) -> list:
        """Get list of supported file types"""
        return list(cls.PARSER_MAP.keys())
    
    @classmethod
    def detect_file_type(cls, file_path: str) -> Optional[str]:
        """
        Detect file type from content analysis
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: Detected file type or None
        """
        path = Path(file_path)
        
        # First try extension
        extension = path.suffix.lstrip('.').lower()
        if extension in cls.PARSER_MAP:
            return extension
        
        # Try to detect from content
        try:
            with open(file_path, 'rb') as f:
                # Read first few bytes
                header = f.read(8)
                
                # Check for Excel file signatures
                if header[:4] == b'\xD0\xCF\x11\xE0':  # Old Excel (.xls)
                    return 'xls'
                elif header[:4] == b'PK\x03\x04':  # ZIP (new Excel .xlsx)
                    return 'xlsx'
                
                # Reset and read as text
                f.seek(0)
                sample = f.read(1024).decode('utf-8', errors='ignore')
                
                # Check for delimiters
                if ',' in sample and sample.count(',') > sample.count('\t'):
                    return 'csv'
                elif '\t' in sample:
                    return 'tsv'
                elif '|' in sample:
                    return 'pipe'
        
        except Exception:
            pass
        
        return None

