"""
AI services module

This module provides AI-powered services for data analysis and mapping:
- LLM provider management (OpenAI, Hugging Face)
- Prompt templates for various tasks
- Mapping recommendation service
- Semantic analysis
"""

from app.services.ai.llm_provider import llm_provider, LLMProvider
from app.services.ai.mapping_service import MappingService

__all__ = [
    'llm_provider',
    'LLMProvider',
    'MappingService',
]
