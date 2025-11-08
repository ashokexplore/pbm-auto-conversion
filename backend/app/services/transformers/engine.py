"""
Data transformation engine core
"""
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import re


class TransformationRule:
    """Represents a single transformation rule"""
    
    def __init__(
        self,
        source_column: str,
        target_column: str,
        transformation_type: str = "direct",
        transformation_func: Optional[Callable] = None,
        parameters: Optional[Dict[str, Any]] = None
    ):
        self.source_column = source_column
        self.target_column = target_column
        self.transformation_type = transformation_type
        self.transformation_func = transformation_func
        self.parameters = parameters or {}
    
    def apply(self, value: Any) -> Any:
        """Apply transformation to a value"""
        if value is None:
            return self.parameters.get('default_value')
        
        if self.transformation_func:
            return self.transformation_func(value, self.parameters)
        
        # Built-in transformations
        if self.transformation_type == "direct":
            return value
        elif self.transformation_type == "uppercase":
            return str(value).upper() if value else None
        elif self.transformation_type == "lowercase":
            return str(value).lower() if value else None
        elif self.transformation_type == "trim":
            return str(value).strip() if value else None
        elif self.transformation_type == "int":
            try:
                return int(float(value)) if value else None
            except (ValueError, TypeError):
                return None
        elif self.transformation_type == "float":
            try:
                return float(value) if value else None
            except (ValueError, TypeError):
                return None
        elif self.transformation_type == "boolean":
            if isinstance(value, bool):
                return value
            str_val = str(value).lower()
            return str_val in ['true', 'yes', '1', 'y']
        elif self.transformation_type == "date":
            # Basic date formatting
            return str(value) if value else None
        else:
            return value


class TransformationEngine:
    """Core transformation engine"""
    
    def __init__(self):
        self.rules: List[TransformationRule] = []
        self.validation_errors: List[Dict[str, Any]] = []
    
    def add_rule(self, rule: TransformationRule):
        """Add a transformation rule"""
        self.rules.append(rule)
    
    def add_rules_from_config(self, mapping_config: Dict[str, Any]):
        """
        Add rules from mapping configuration
        
        Args:
            mapping_config: Mapping configuration with rules
        """
        mappings = mapping_config.get("mappings", [])
        
        for mapping in mappings:
            source = mapping.get("input_column")
            target = mapping.get("reference_column") or mapping.get("target_column")
            transform_type = mapping.get("transformation", "direct")
            
            if source and target:
                rule = TransformationRule(
                    source_column=source,
                    target_column=target,
                    transformation_type=transform_type
                )
                self.add_rule(rule)
    
    def transform_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a single row of data
        
        Args:
            row: Input row
            
        Returns:
            Transformed row
        """
        transformed = {}
        
        for rule in self.rules:
            source_value = row.get(rule.source_column)
            transformed_value = rule.apply(source_value)
            transformed[rule.target_column] = transformed_value
        
        return transformed
    
    def transform_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform multiple rows of data
        
        Args:
            data: List of input rows
            
        Returns:
            List of transformed rows
        """
        transformed_data = []
        
        for idx, row in enumerate(data):
            try:
                transformed_row = self.transform_row(row)
                transformed_data.append(transformed_row)
            except Exception as e:
                self.validation_errors.append({
                    "row_index": idx,
                    "error": str(e),
                    "row_data": row
                })
        
        return transformed_data
    
    def get_validation_errors(self) -> List[Dict[str, Any]]:
        """Get list of validation errors"""
        return self.validation_errors
    
    def clear_errors(self):
        """Clear validation errors"""
        self.validation_errors = []


class DataValidator:
    """Data validation utilities"""
    
    @staticmethod
    def validate_required(value: Any, field_name: str) -> Optional[str]:
        """Validate required field"""
        if value is None or value == '':
            return f"{field_name} is required"
        return None
    
    @staticmethod
    def validate_type(value: Any, expected_type: str, field_name: str) -> Optional[str]:
        """Validate data type"""
        if value is None:
            return None
        
        try:
            if expected_type == "integer":
                int(value)
            elif expected_type == "float":
                float(value)
            elif expected_type == "boolean":
                if not isinstance(value, bool):
                    str_val = str(value).lower()
                    if str_val not in ['true', 'false', 'yes', 'no', '1', '0']:
                        return f"{field_name} must be a boolean value"
            return None
        except (ValueError, TypeError):
            return f"{field_name} must be of type {expected_type}"
    
    @staticmethod
    def validate_range(
        value: Any,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        field_name: str = "Field"
    ) -> Optional[str]:
        """Validate numeric range"""
        if value is None:
            return None
        
        try:
            num_value = float(value)
            if min_value is not None and num_value < min_value:
                return f"{field_name} must be >= {min_value}"
            if max_value is not None and num_value > max_value:
                return f"{field_name} must be <= {max_value}"
            return None
        except (ValueError, TypeError):
            return f"{field_name} must be numeric"
    
    @staticmethod
    def validate_pattern(value: Any, pattern: str, field_name: str) -> Optional[str]:
        """Validate against regex pattern"""
        if value is None:
            return None
        
        if not re.match(pattern, str(value)):
            return f"{field_name} does not match required pattern"
        return None
    
    @staticmethod
    def validate_length(
        value: Any,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        field_name: str = "Field"
    ) -> Optional[str]:
        """Validate string length"""
        if value is None:
            return None
        
        str_value = str(value)
        if min_length is not None and len(str_value) < min_length:
            return f"{field_name} must be at least {min_length} characters"
        if max_length is not None and len(str_value) > max_length:
            return f"{field_name} must be at most {max_length} characters"
        return None

