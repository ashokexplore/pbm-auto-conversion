"""
Flat file (position-based/fixed-width) parser
"""
from typing import Dict, Any, List, Optional
import re

from app.services.parsers.base import BaseParser, ParseResult


class FieldDefinition:
    """Definition for a fixed-width field"""
    
    def __init__(self, name: str, start: int, end: int, data_type: str = 'string'):
        self.name = name
        self.start = start  # 0-based start position
        self.end = end      # 0-based end position (exclusive)
        self.data_type = data_type
        
    def extract(self, line: str) -> str:
        """Extract field value from line"""
        return line[self.start:self.end].strip()


class FlatFileParser(BaseParser):
    """Parser for flat files (position-based/fixed-width)"""
    
    def __init__(self, file_path: str, layout: Optional[List[FieldDefinition]] = None):
        super().__init__(file_path)
        self.layout = layout or []
        self.encoding = 'utf-8'
        
    def detect_encoding(self) -> str:
        """Detect file encoding"""
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(self.file_path, 'r', encoding=encoding) as f:
                    f.read(1024)
                return encoding
            except UnicodeDecodeError:
                continue
        
        return 'utf-8'
    
    def auto_detect_layout(self, sample_lines: List[str]) -> List[FieldDefinition]:
        """
        Auto-detect field positions based on consistent spacing
        
        Args:
            sample_lines: Sample lines to analyze
            
        Returns:
            List[FieldDefinition]: Detected field definitions
        """
        if not sample_lines or len(sample_lines) < 2:
            return []
        
        # Assume first line might be header
        header_line = sample_lines[0]
        
        # Find column boundaries by looking for consistent spacing
        # This is a simple heuristic - look for 2+ spaces that appear in all lines
        potential_breaks = []
        
        for i in range(len(header_line) - 1):
            # Check if position i has space in all sample lines
            if all(i < len(line) and line[i:i+2] == '  ' for line in sample_lines[:5]):
                potential_breaks.append(i)
        
        # Remove consecutive breaks
        breaks = [0]  # Start
        for i in range(len(potential_breaks)):
            if i == 0 or potential_breaks[i] > potential_breaks[i-1] + 2:
                breaks.append(potential_breaks[i])
        breaks.append(len(header_line))  # End
        
        # Create field definitions
        fields = []
        for i in range(len(breaks) - 1):
            start = breaks[i]
            end = breaks[i + 1]
            
            # Extract field name from header
            field_name = header_line[start:end].strip()
            if not field_name:
                field_name = f"field_{i+1}"
            
            fields.append(FieldDefinition(field_name, start, end))
        
        return fields
    
    def set_layout(self, layout: List[Dict[str, Any]]):
        """
        Set field layout from dictionary format
        
        Args:
            layout: List of field definitions as dicts
                    Each dict should have: name, start, end, type (optional)
        """
        self.layout = [
            FieldDefinition(
                name=field['name'],
                start=field['start'],
                end=field['end'],
                data_type=field.get('type', 'string')
            )
            for field in layout
        ]
    
    def parse(self, skip_header: bool = False) -> ParseResult:
        """
        Parse flat file
        
        Args:
            skip_header: Whether to skip first line as header
            
        Returns:
            ParseResult: Parsed data
        """
        # Detect encoding
        self.encoding = self.detect_encoding()
        
        # Read file
        with open(self.file_path, 'r', encoding=self.encoding, errors='ignore') as f:
            lines = [line.rstrip('\n\r') for line in f.readlines()]
        
        # Auto-detect layout if not provided
        if not self.layout:
            self.layout = self.auto_detect_layout(lines)
        
        if not self.layout:
            raise ValueError("Could not detect field layout. Please provide layout definition.")
        
        # Parse data
        headers = [field.name for field in self.layout]
        data = []
        
        start_line = 1 if skip_header else 0
        for line in lines[start_line:]:
            if line.strip():  # Skip empty lines
                row = {}
                for field in self.layout:
                    value = field.extract(line)
                    row[field.name] = value
                data.append(row)
        
        metadata = {
            "file_type": "flat_file",
            "encoding": self.encoding,
            "layout": [
                {
                    "name": f.name,
                    "start": f.start,
                    "end": f.end,
                    "length": f.end - f.start,
                    "type": f.data_type
                }
                for f in self.layout
            ],
            "row_count": len(data),
            "column_count": len(headers),
            "columns": headers,
            "file_info": self.get_file_info()
        }
        
        return ParseResult(
            data=data,
            headers=headers,
            metadata=metadata
        )
    
    def detect_structure(self) -> Dict[str, Any]:
        """Detect flat file structure"""
        result = self.parse()
        
        # Analyze data types
        column_types = {}
        column_samples = {}
        
        for header in result.headers:
            values = [row.get(header) for row in result.data if row.get(header)]
            
            if values:
                sample_types = [self.infer_data_type(v) for v in values[:100]]
                most_common = max(set(sample_types), key=sample_types.count)
                column_types[header] = most_common
                column_samples[header] = values[:5]
            else:
                column_types[header] = 'null'
                column_samples[header] = []
        
        return {
            "file_type": "flat_file",
            "encoding": self.encoding,
            "layout": result.metadata["layout"],
            "columns": result.headers,
            "column_types": column_types,
            "column_samples": column_samples,
            "row_count": len(result.data),
            "column_count": len(result.headers)
        }

