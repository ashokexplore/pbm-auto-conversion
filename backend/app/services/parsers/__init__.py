"""
File parsers module

This module provides parsers for various file formats:
- CSV: Comma-separated values
- Excel: .xls and .xlsx files
- TXT: Text files (structured and unstructured)
- Pipe Delimited: Custom delimiter files (pipe, tab, semicolon, etc.)
- Flat File: Position-based/fixed-width files
"""

from app.services.parsers.base import BaseParser, ParseResult
from app.services.parsers.factory import ParserFactory
from app.services.parsers.csv_parser import CSVParser
from app.services.parsers.excel_parser import ExcelParser
from app.services.parsers.txt_parser import TXTParser
from app.services.parsers.pipe_parser import PipeDelimitedParser
from app.services.parsers.flat_file_parser import FlatFileParser, FieldDefinition

__all__ = [
    'BaseParser',
    'ParseResult',
    'ParserFactory',
    'CSVParser',
    'ExcelParser',
    'TXTParser',
    'PipeDelimitedParser',
    'FlatFileParser',
    'FieldDefinition',
]


