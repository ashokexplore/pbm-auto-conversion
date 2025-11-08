"""
Prompt templates for AI-powered analysis
"""
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from typing import Dict, List, Any


# Column mapping prompt
COLUMN_MAPPING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert data analyst specializing in data mapping and transformation.
Your task is to analyze two file structures and recommend column mappings from the input file to the reference file.

Consider:
1. Semantic similarity (e.g., "customer_name" maps to "client_name")
2. Data type compatibility
3. Sample data patterns
4. Business logic (e.g., "first_name" + "last_name" could map to "full_name")

Provide confidence scores (0-100) for each mapping recommendation."""),
    ("human", """Input File Structure:
Columns: {input_columns}
Data Types: {input_types}
Sample Data: {input_samples}

Reference File Structure:
Columns: {reference_columns}
Data Types: {reference_types}
Sample Data: {reference_samples}

Analyze and provide mapping recommendations in JSON format:
{{
  "mappings": [
    {{
      "input_column": "column_name",
      "reference_column": "target_column",
      "confidence": 95,
      "reasoning": "Explanation for this mapping",
      "transformation": "none|rename|concat|split|custom",
      "transformation_logic": "Detailed transformation steps if needed"
    }}
  ],
  "unmapped_input_columns": ["col1", "col2"],
  "unmapped_reference_columns": ["col3", "col4"],
  "overall_confidence": 85
}}""")
])


# Data type inference prompt
DATA_TYPE_INFERENCE_PROMPT = PromptTemplate(
    input_variables=["column_name", "sample_values"],
    template="""Analyze the following column and infer its data type:

Column Name: {column_name}
Sample Values: {sample_values}

Determine the most appropriate data type from:
- integer
- float
- boolean
- date
- datetime
- string
- email
- phone
- currency
- percentage

Respond with just the data type name."""
)


# Transformation logic prompt
TRANSFORMATION_LOGIC_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert in data transformation logic.
Generate clear, executable transformation rules for converting data from one format to another."""),
    ("human", """Source Column: {source_column}
Source Type: {source_type}
Source Samples: {source_samples}

Target Column: {target_column}
Target Type: {target_type}
Target Samples: {target_samples}

Generate transformation logic in JSON format:
{{
  "transformation_type": "rename|convert|concat|split|calculate|custom",
  "steps": [
    "Step 1 description",
    "Step 2 description"
  ],
  "validation_rules": ["rule1", "rule2"],
  "example_input": "sample input",
  "example_output": "expected output"
}}""")
])


# Field structure analysis prompt
FIELD_ANALYSIS_PROMPT = PromptTemplate(
    input_variables=["file_content", "file_type"],
    template="""Analyze this {file_type} file structure and identify:

File Content Sample:
{file_content}

Provide analysis in JSON format:
{{
  "detected_delimiter": "delimiter character or null",
  "has_header": true/false,
  "estimated_columns": number,
  "column_names": ["col1", "col2", ...],
  "data_patterns": {{
    "col1": "pattern description",
    "col2": "pattern description"
  }}
}}"""
)


# Validation rules generation prompt
VALIDATION_RULES_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert in data quality and validation.
Generate comprehensive validation rules based on sample data and business logic."""),
    ("human", """Column: {column_name}
Data Type: {data_type}
Sample Values: {sample_values}
Statistics: {statistics}

Generate validation rules in JSON format:
{{
  "rules": [
    {{
      "type": "required|range|pattern|length|custom",
      "rule": "Rule description",
      "error_message": "Message when validation fails"
    }}
  ],
  "constraints": {{
    "min": value,
    "max": value,
    "pattern": "regex pattern",
    "allowed_values": ["value1", "value2"]
  }}
}}""")
])


# Similarity calculation prompt
SEMANTIC_SIMILARITY_PROMPT = PromptTemplate(
    input_variables=["column1", "column2", "context"],
    template="""Calculate semantic similarity between these two column names:

Column 1: {column1}
Column 2: {column2}
Context: {context}

Consider:
- Synonyms (e.g., "customer" and "client")
- Abbreviations (e.g., "addr" and "address")
- Common business terms
- Domain-specific terminology

Respond with a similarity score from 0-100 and brief reasoning:
{{
  "similarity_score": number,
  "reasoning": "explanation"
}}"""
)


def get_column_mapping_prompt() -> ChatPromptTemplate:
    """Get column mapping prompt template"""
    return COLUMN_MAPPING_PROMPT


def get_data_type_inference_prompt() -> PromptTemplate:
    """Get data type inference prompt template"""
    return DATA_TYPE_INFERENCE_PROMPT


def get_transformation_logic_prompt() -> ChatPromptTemplate:
    """Get transformation logic prompt template"""
    return TRANSFORMATION_LOGIC_PROMPT


def get_field_analysis_prompt() -> PromptTemplate:
    """Get field analysis prompt template"""
    return FIELD_ANALYSIS_PROMPT


def get_validation_rules_prompt() -> ChatPromptTemplate:
    """Get validation rules prompt template"""
    return VALIDATION_RULES_PROMPT


def get_semantic_similarity_prompt() -> PromptTemplate:
    """Get semantic similarity prompt template"""
    return SEMANTIC_SIMILARITY_PROMPT

