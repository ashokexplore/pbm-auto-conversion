"""
Excel file parser (.xls, .xlsx)
"""
import pandas as pd
from typing import Dict, Any, List

from app.services.parsers.base import BaseParser, ParseResult


class ExcelParser(BaseParser):
    """Parser for Excel files"""
    
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.sheet_name = 0  # Default to first sheet
        
    def get_sheet_names(self) -> List[str]:
        """
        Get all sheet names in Excel file
        
        Returns:
            List[str]: Sheet names
        """
        try:
            xls = pd.ExcelFile(self.file_path)
            return xls.sheet_names
        except Exception as e:
            raise ValueError(f"Failed to read Excel file: {str(e)}")
    
    def parse(self, sheet_name: Any = 0) -> ParseResult:
        """
        Parse Excel file
        
        Args:
            sheet_name: Sheet name or index to parse (default: 0)
            
        Returns:
            ParseResult: Parsed data
        """
        try:
            # Read Excel file
            df = pd.read_excel(
                self.file_path,
                sheet_name=sheet_name,
                engine='openpyxl' if self.file_path.suffix == '.xlsx' else 'xlrd'
            )
            
            # Convert to list of dictionaries
            data = df.to_dict('records')
            headers = df.columns.tolist()
            
            # Get sheet names
            sheet_names = self.get_sheet_names()
            
            # Get metadata
            metadata = {
                "file_type": "excel",
                "extension": self.file_path.suffix,
                "sheet_names": sheet_names,
                "active_sheet": sheet_name if isinstance(sheet_name, str) else sheet_names[sheet_name],
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
            raise ValueError(f"Failed to parse Excel file: {str(e)}")
    
    def parse_all_sheets(self) -> Dict[str, ParseResult]:
        """
        Parse all sheets in Excel file
        
        Returns:
            Dict[str, ParseResult]: Dictionary of sheet name to ParseResult
        """
        sheet_names = self.get_sheet_names()
        results = {}
        
        for sheet_name in sheet_names:
            try:
                results[sheet_name] = self.parse(sheet_name=sheet_name)
            except Exception as e:
                print(f"Failed to parse sheet {sheet_name}: {str(e)}")
        
        return results
    
    def detect_structure(self) -> Dict[str, Any]:
        """Detect Excel structure and data types"""
        # Parse first sheet
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
            "file_type": "excel",
            "extension": self.file_path.suffix,
            "sheet_names": self.get_sheet_names(),
            "columns": result.headers,
            "column_types": column_types,
            "column_samples": column_samples,
            "row_count": len(result.data),
            "column_count": len(result.headers)
        }

