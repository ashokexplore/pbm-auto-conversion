"""
Pipe-delimited file parser (also handles TSV and other delimited formats)
"""
import pandas as pd
from typing import Dict, Any, Optional

from app.services.parsers.base import BaseParser, ParseResult


class PipeDelimitedParser(BaseParser):
    """Parser for pipe-delimited and other custom delimited files"""
    
    def __init__(self, file_path: str, delimiter: str = '|'):
        super().__init__(file_path)
        self.delimiter = delimiter
        self.has_header = True
        
    def detect_delimiter(self) -> str:
        """
        Detect delimiter from file content
        
        Returns:
            str: Detected delimiter
        """
        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            sample = f.read(8192)
        
        # Count common delimiters
        delimiters = {
            '|': sample.count('|'),
            '\t': sample.count('\t'),
            ';': sample.count(';'),
            ':': sample.count(':'),
        }
        
        # Return most common
        return max(delimiters, key=delimiters.get)
    
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
    
    def parse(self, delimiter: Optional[str] = None) -> ParseResult:
        """
        Parse delimited file
        
        Args:
            delimiter: Optional delimiter override
            
        Returns:
            ParseResult: Parsed data
        """
        # Use provided delimiter or detect
        if delimiter:
            self.delimiter = delimiter
        elif self.delimiter == '|':  # If still default, try to detect
            self.delimiter = self.detect_delimiter()
        
        # Detect encoding
        encoding = self.detect_encoding()
        
        try:
            # Read with pandas
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
                "file_type": "pipe_delimited" if self.delimiter == '|' else "delimited",
                "delimiter": self.delimiter,
                "delimiter_name": self._get_delimiter_name(),
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
            raise ValueError(f"Failed to parse delimited file: {str(e)}")
    
    def _get_delimiter_name(self) -> str:
        """Get human-readable delimiter name"""
        names = {
            '|': 'pipe',
            '\t': 'tab',
            ';': 'semicolon',
            ':': 'colon',
            ',': 'comma'
        }
        return names.get(self.delimiter, 'custom')
    
    def detect_structure(self) -> Dict[str, Any]:
        """Detect file structure and data types"""
        result = self.parse()
        
        # Analyze data types
        column_types = {}
        column_samples = {}
        
        for header in result.headers:
            values = [row.get(header) for row in result.data if row.get(header) is not None]
            
            if values:
                sample_types = [self.infer_data_type(v) for v in values[:100]]
                most_common = max(set(sample_types), key=sample_types.count)
                column_types[header] = most_common
                column_samples[header] = values[:5]
            else:
                column_types[header] = 'null'
                column_samples[header] = []
        
        return {
            "file_type": "delimited",
            "delimiter": self.delimiter,
            "delimiter_name": self._get_delimiter_name(),
            "has_header": self.has_header,
            "columns": result.headers,
            "column_types": column_types,
            "column_samples": column_samples,
            "row_count": len(result.data),
            "column_count": len(result.headers)
        }

