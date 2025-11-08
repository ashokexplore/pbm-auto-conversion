"""
AI-powered mapping recommendation service
"""
from typing import Dict, List, Any, Optional
import json
from langchain.chains import LLMChain

from app.services.ai.llm_provider import llm_provider
from app.services.ai.prompts import (
    get_column_mapping_prompt,
    get_semantic_similarity_prompt,
    get_transformation_logic_prompt,
    get_validation_rules_prompt
)


class MappingService:
    """Service for AI-powered column mapping recommendations"""
    
    def __init__(self, provider: Optional[str] = None):
        self.provider = provider
        
    async def generate_mappings(
        self,
        input_structure: Dict[str, Any],
        reference_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate column mapping recommendations
        
        Args:
            input_structure: Input file structure
            reference_structure: Reference file structure
            
        Returns:
            Dict: Mapping recommendations with confidence scores
        """
        try:
            # Get LLM model
            llm = llm_provider.get_model(self.provider, temperature=0.1)
            
            # Prepare data for prompt
            input_columns = input_structure.get("columns", [])
            input_types = input_structure.get("column_types", {})
            input_samples = input_structure.get("column_samples", {})
            
            reference_columns = reference_structure.get("columns", [])
            reference_types = reference_structure.get("column_types", {})
            reference_samples = reference_structure.get("column_samples", {})
            
            # Create chain
            prompt = get_column_mapping_prompt()
            
            # Invoke LLM
            response = await llm.ainvoke(prompt.format_messages(
                input_columns=", ".join(input_columns),
                input_types=json.dumps(input_types, indent=2),
                input_samples=json.dumps(input_samples, indent=2),
                reference_columns=", ".join(reference_columns),
                reference_types=json.dumps(reference_types, indent=2),
                reference_samples=json.dumps(reference_samples, indent=2)
            ))
            
            # Parse response
            result = self._parse_json_response(response.content)
            
            return result
        
        except Exception as e:
            # Fallback to rule-based matching
            print(f"AI mapping failed, using fallback: {str(e)}")
            return self._fallback_mapping(input_structure, reference_structure)
    
    async def calculate_similarity(
        self,
        column1: str,
        column2: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Calculate semantic similarity between two column names
        
        Args:
            column1: First column name
            column2: Second column name
            context: Optional context information
            
        Returns:
            Dict: Similarity score and reasoning
        """
        try:
            llm = llm_provider.get_model(self.provider, temperature=0.0)
            prompt = get_semantic_similarity_prompt()
            
            response = await llm.ainvoke(
                prompt.format(
                    column1=column1,
                    column2=column2,
                    context=context
                )
            )
            
            return self._parse_json_response(response.content)
        
        except Exception as e:
            # Fallback to simple string similarity
            return self._simple_similarity(column1, column2)
    
    async def generate_transformation_logic(
        self,
        source_column: str,
        source_type: str,
        source_samples: List[Any],
        target_column: str,
        target_type: str,
        target_samples: List[Any]
    ) -> Dict[str, Any]:
        """
        Generate transformation logic between columns
        
        Args:
            source_column: Source column name
            source_type: Source data type
            source_samples: Source sample values
            target_column: Target column name
            target_type: Target data type
            target_samples: Target sample values
            
        Returns:
            Dict: Transformation logic
        """
        try:
            llm = llm_provider.get_model(self.provider, temperature=0.2)
            prompt = get_transformation_logic_prompt()
            
            response = await llm.ainvoke(prompt.format_messages(
                source_column=source_column,
                source_type=source_type,
                source_samples=json.dumps(source_samples),
                target_column=target_column,
                target_type=target_type,
                target_samples=json.dumps(target_samples)
            ))
            
            return self._parse_json_response(response.content)
        
        except Exception as e:
            # Fallback to basic transformation
            return self._basic_transformation(source_type, target_type)
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from LLM"""
        try:
            # Try to find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
            else:
                return {"error": "No JSON found in response", "raw": response}
        
        except json.JSONDecodeError:
            return {"error": "Invalid JSON in response", "raw": response}
    
    def _fallback_mapping(
        self,
        input_structure: Dict[str, Any],
        reference_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Rule-based fallback mapping"""
        input_columns = input_structure.get("columns", [])
        reference_columns = reference_structure.get("columns", [])
        
        mappings = []
        mapped_inputs = set()
        mapped_references = set()
        
        # Exact matches
        for input_col in input_columns:
            if input_col in reference_columns:
                mappings.append({
                    "input_column": input_col,
                    "reference_column": input_col,
                    "confidence": 100,
                    "reasoning": "Exact name match",
                    "transformation": "none"
                })
                mapped_inputs.add(input_col)
                mapped_references.add(input_col)
        
        # Case-insensitive matches
        for input_col in input_columns:
            if input_col in mapped_inputs:
                continue
            
            input_lower = input_col.lower().replace('_', '').replace(' ', '')
            
            for ref_col in reference_columns:
                if ref_col in mapped_references:
                    continue
                
                ref_lower = ref_col.lower().replace('_', '').replace(' ', '')
                
                if input_lower == ref_lower:
                    mappings.append({
                        "input_column": input_col,
                        "reference_column": ref_col,
                        "confidence": 90,
                        "reasoning": "Case-insensitive match",
                        "transformation": "rename"
                    })
                    mapped_inputs.add(input_col)
                    mapped_references.add(ref_col)
                    break
        
        return {
            "mappings": mappings,
            "unmapped_input_columns": [c for c in input_columns if c not in mapped_inputs],
            "unmapped_reference_columns": [c for c in reference_columns if c not in mapped_references],
            "overall_confidence": len(mappings) / max(len(input_columns), 1) * 100,
            "fallback_used": True
        }
    
    def _simple_similarity(self, col1: str, col2: str) -> Dict[str, Any]:
        """Simple string similarity calculation"""
        # Normalize
        c1 = col1.lower().replace('_', '').replace(' ', '')
        c2 = col2.lower().replace('_', '').replace(' ', '')
        
        # Exact match
        if c1 == c2:
            return {"similarity_score": 100, "reasoning": "Exact match (case-insensitive)"}
        
        # Substring match
        if c1 in c2 or c2 in c1:
            return {"similarity_score": 75, "reasoning": "Substring match"}
        
        # Levenshtein-like simple comparison
        common_chars = sum(1 for a, b in zip(c1, c2) if a == b)
        max_len = max(len(c1), len(c2))
        score = (common_chars / max_len * 100) if max_len > 0 else 0
        
        return {"similarity_score": int(score), "reasoning": "Character-based similarity"}
    
    def _basic_transformation(self, source_type: str, target_type: str) -> Dict[str, Any]:
        """Basic transformation logic"""
        if source_type == target_type:
            return {
                "transformation_type": "none",
                "steps": ["No transformation needed"],
                "validation_rules": []
            }
        
        return {
            "transformation_type": "convert",
            "steps": [f"Convert {source_type} to {target_type}"],
            "validation_rules": [f"Ensure value is valid {target_type}"]
        }

