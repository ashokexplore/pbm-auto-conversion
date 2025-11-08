"""
CSV file parser
"""
import pandas as pd
from typing import Dict, Any, List
import csv

from app.services.parsers.base import BaseParser, ParseResult


class CSVParser(BaseParser):
    """Parser for CSV files"""
    
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.delimiter = None
        self.has_header = True
        
    def detect_delimiter(self) -> str:
        """
        Detect CSV delimiter
        
        Returns:
            str: Detected delimiter
        """
        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            sample = f.read(8192)
            
        sniffer = csv.Sniffer()
        try:
            dialect = sniffer.sniff(sample)
            return dialect.delimiter
        except:
            # Default to comma
            return ','
    
    def detect_encoding(self) -> str:
        """
        Detect file encoding
        
        Returns:
            str: Detected encoding
        """
        # Try common encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(self.file_path, 'r', encoding=encoding) as f:
                    f.read(1024)
                return encoding
            except UnicodeDecodeError:
                continue
        
        return 'utf-8'  # Default
    
    def parse(self) -> ParseResult:
        """Parse CSV file"""
        # Detect delimiter if not set
        if not self.delimiter:
            self.delimiter = self.detect_delimiter()
        
        # Detect encoding
        encoding = self.detect_encoding()
        
        # Read CSV with pandas
        try:
            df = pd.read_csv(
                self.file_path,
                delimiter=self.delimiter,
                encoding=encoding,
                engine='python',
                on_bad_lines='skip'
            )
            
            # Convert to list of dictionaries
            data = df.to_dict('records')
            headers = df.columns.tolist()
            
            # Get metadata
            metadata = {
                "file_type": "csv",
                "delimiter": self.delimiter,
                "encoding": encoding,
                "row_count": len(df),
                "column_count": len(headers),
                "columns": headers,
                "file_info": self.get_file_info()
            }
            
            return ParseResult(
                data=data,
                headers=headers,
                metadata=metadata
            )
        
        except Exception as e:
            raise ValueError(f"Failed to parse CSV file: {str(e)}")
    
    def detect_structure(self) -> Dict[str, Any]:
        """Detect CSV structure and data types"""
        # Parse file first
        result = self.parse()
        
        # Analyze data types for each column
        column_types = {}
        column_samples = {}
        
        for header in result.headers:
            # Get sample values (non-null)
            values = [row.get(header) for row in result.data if row.get(header) is not None]
            
            if values:
                # Infer type from first few values
                sample_types = [self.infer_data_type(v) for v in values[:100]]
                # Most common type
                most_common = max(set(sample_types), key=sample_types.count)
                column_types[header] = most_common
                
                # Store sample values
                column_samples[header] = values[:5]
            else:
                column_types[header] = 'null'
                column_samples[header] = []
        
        return {
            "file_type": "csv",
            "delimiter": self.delimiter,
            "has_header": self.has_header,
            "columns": result.headers,
            "column_types": column_types,
            "column_samples": column_samples,
            "row_count": len(result.data),
            "column_count": len(result.headers)
        }

