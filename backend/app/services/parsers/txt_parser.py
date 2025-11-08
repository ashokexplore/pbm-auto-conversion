"""
Text file parser
"""
from typing import Dict, Any, List
import re

from app.services.parsers.base import BaseParser, ParseResult


class TXTParser(BaseParser):
    """Parser for text files"""
    
    def __init__(self, file_path: str):
        super().__init__(file_path)
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
    
    def detect_structure_type(self, lines: List[str]) -> str:
        """
        Detect if text file has structure (delimited, fixed-width, etc.)
        
        Args:
            lines: Sample lines from file
            
        Returns:
            str: Structure type
        """
        if not lines:
            return 'unstructured'
        
        # Check for common delimiters
        sample = '\n'.join(lines[:10])
        
        if ',' in sample:
            return 'csv'
        elif '\t' in sample:
            return 'tsv'
        elif '|' in sample:
            return 'pipe_delimited'
        elif all(len(line) == len(lines[0]) for line in lines[:10]):
            return 'fixed_width'
        else:
            return 'unstructured'
    
    def parse(self) -> ParseResult:
        """Parse text file"""
        # Detect encoding
        self.encoding = self.detect_encoding()
        
        # Read file
        with open(self.file_path, 'r', encoding=self.encoding, errors='ignore') as f:
            lines = [line.rstrip('\n\r') for line in f.readlines()]
        
        # Detect structure
        structure_type = self.detect_structure_type(lines)
        
        # Convert to structured data
        data = []
        headers = []
        
        if structure_type in ['csv', 'tsv', 'pipe_delimited']:
            # Treat as delimited file
            delimiter = ',' if structure_type == 'csv' else '\t' if structure_type == 'tsv' else '|'
            
            if lines:
                # Assume first line is header
                headers = lines[0].split(delimiter)
                
                for line in lines[1:]:
                    values = line.split(delimiter)
                    if len(values) == len(headers):
                        data.append(dict(zip(headers, values)))
        else:
            # Unstructured - treat each line as a row
            headers = ['line_number', 'content']
            for i, line in enumerate(lines, 1):
                data.append({
                    'line_number': i,
                    'content': line
                })
        
        metadata = {
            "file_type": "text",
            "encoding": self.encoding,
            "structure_type": structure_type,
            "line_count": len(lines),
            "columns": headers,
            "file_info": self.get_file_info()
        }
        
        return ParseResult(
            data=data,
            headers=headers,
            metadata=metadata
        )
    
    def detect_structure(self) -> Dict[str, Any]:
        """Detect text file structure"""
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
            "file_type": "text",
            "encoding": self.encoding,
            "structure_type": result.metadata.get("structure_type"),
            "columns": result.headers,
            "column_types": column_types,
            "column_samples": column_samples,
            "line_count": len(result.data)
        }

