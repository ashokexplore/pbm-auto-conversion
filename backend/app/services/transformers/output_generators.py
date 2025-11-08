"""
Output format generators for various file formats
"""
from typing import List, Dict, Any
import pandas as pd
import json
import csv
from io import StringIO, BytesIO
from pathlib import Path


class BaseOutputGenerator:
    """Base class for output generators"""
    
    def __init__(self, data: List[Dict[str, Any]], headers: List[str]):
        self.data = data
        self.headers = headers
    
    def generate(self, output_path: str) -> str:
        """Generate output file"""
        raise NotImplementedError


class CSVOutputGenerator(BaseOutputGenerator):
    """CSV output generator"""
    
    def generate(self, output_path: str, delimiter: str = ',') -> str:
        """
        Generate CSV file
        
        Args:
            output_path: Output file path
            delimiter: CSV delimiter
            
        Returns:
            Path to generated file
        """
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.headers, delimiter=delimiter)
            writer.writeheader()
            writer.writerows(self.data)
        
        return output_path


class ExcelOutputGenerator(BaseOutputGenerator):
    """Excel output generator"""
    
    def generate(self, output_path: str, sheet_name: str = 'Sheet1') -> str:
        """
        Generate Excel file
        
        Args:
            output_path: Output file path
            sheet_name: Sheet name
            
        Returns:
            Path to generated file
        """
        df = pd.DataFrame(self.data, columns=self.headers)
        df.to_excel(output_path, sheet_name=sheet_name, index=False, engine='openpyxl')
        return output_path


class JSONOutputGenerator(BaseOutputGenerator):
    """JSON output generator"""
    
    def generate(self, output_path: str, pretty: bool = True) -> str:
        """
        Generate JSON file
        
        Args:
            output_path: Output file path
            pretty: Whether to format with indentation
            
        Returns:
            Path to generated file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(self.data, f, ensure_ascii=False)
        
        return output_path


class TSVOutputGenerator(BaseOutputGenerator):
    """TSV (Tab-separated) output generator"""
    
    def generate(self, output_path: str) -> str:
        """Generate TSV file"""
        csv_gen = CSVOutputGenerator(self.data, self.headers)
        return csv_gen.generate(output_path, delimiter='\t')


class PipeDelimitedOutputGenerator(BaseOutputGenerator):
    """Pipe-delimited output generator"""
    
    def generate(self, output_path: str, delimiter: str = '|') -> str:
        """Generate pipe-delimited file"""
        csv_gen = CSVOutputGenerator(self.data, self.headers)
        return csv_gen.generate(output_path, delimiter=delimiter)


class FixedWidthOutputGenerator(BaseOutputGenerator):
    """Fixed-width/flat file output generator"""
    
    def __init__(
        self,
        data: List[Dict[str, Any]],
        headers: List[str],
        column_widths: Dict[str, int]
    ):
        super().__init__(data, headers)
        self.column_widths = column_widths
    
    def generate(self, output_path: str) -> str:
        """
        Generate fixed-width file
        
        Args:
            output_path: Output file path
            
        Returns:
            Path to generated file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header
            header_line = ''
            for header in self.headers:
                width = self.column_widths.get(header, 20)
                header_line += header.ljust(width)
            f.write(header_line + '\n')
            
            # Write data
            for row in self.data:
                line = ''
                for header in self.headers:
                    width = self.column_widths.get(header, 20)
                    value = str(row.get(header, ''))
                    line += value.ljust(width)[:width]  # Truncate if too long
                f.write(line + '\n')
        
        return output_path


class OutputGeneratorFactory:
    """Factory for creating output generators"""
    
    GENERATORS = {
        'csv': CSVOutputGenerator,
        'excel': ExcelOutputGenerator,
        'xlsx': ExcelOutputGenerator,
        'xls': ExcelOutputGenerator,
        'json': JSONOutputGenerator,
        'tsv': TSVOutputGenerator,
        'pipe': PipeDelimitedOutputGenerator,
        'fixed': FixedWidthOutputGenerator,
        'txt': CSVOutputGenerator,  # Default to CSV for txt
    }
    
    @classmethod
    def create_generator(
        cls,
        output_format: str,
        data: List[Dict[str, Any]],
        headers: List[str],
        **kwargs
    ) -> BaseOutputGenerator:
        """
        Create output generator for specified format
        
        Args:
            output_format: Output format (csv, excel, json, etc.)
            data: Data to output
            headers: Column headers
            **kwargs: Additional arguments for generator
            
        Returns:
            Output generator instance
        """
        generator_class = cls.GENERATORS.get(output_format.lower())
        
        if not generator_class:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        # Special handling for fixed-width
        if output_format.lower() == 'fixed':
            column_widths = kwargs.get('column_widths', {})
            return generator_class(data, headers, column_widths)
        
        return generator_class(data, headers)
    
    @classmethod
    def get_supported_formats(cls) -> List[str]:
        """Get list of supported output formats"""
        return list(cls.GENERATORS.keys())

