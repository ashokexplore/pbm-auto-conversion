"""
LLM provider configuration and management
"""
from typing import Optional, Union
from langchain_openai import ChatOpenAI
from langchain_community.llms import HuggingFaceHub
from langchain.schema import BaseLanguageModel
import os

from app.core.config import settings


class LLMProvider:
    """LLM provider manager with fallback support"""
    
    def __init__(self):
        self.primary_provider = "openai"
        self.fallback_provider = "huggingface"
        self._openai_model = None
        self._huggingface_model = None
        
    def get_openai_model(self, temperature: float = 0.0) -> Optional[ChatOpenAI]:
        """
        Get OpenAI model instance
        
        Args:
            temperature: Model temperature (0-1)
            
        Returns:
            ChatOpenAI instance or None if not configured
        """
        if not settings.OPENAI_API_KEY:
            return None
        
        try:
            return ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=temperature,
                openai_api_key=settings.OPENAI_API_KEY
            )
        except Exception as e:
            print(f"Failed to initialize OpenAI: {str(e)}")
            return None
    
    def get_huggingface_model(self, temperature: float = 0.0) -> Optional[HuggingFaceHub]:
        """
        Get Hugging Face model instance
        
        Args:
            temperature: Model temperature (0-1)
            
        Returns:
            HuggingFaceHub instance or None if not configured
        """
        if not settings.HUGGINGFACE_API_KEY:
            return None
        
        try:
            return HuggingFaceHub(
                repo_id="mistralai/Mistral-7B-Instruct-v0.2",
                huggingfacehub_api_token=settings.HUGGINGFACE_API_KEY,
                model_kwargs={"temperature": temperature, "max_length": 2048}
            )
        except Exception as e:
            print(f"Failed to initialize Hugging Face: {str(e)}")
            return None
    
    def get_model(self, 
                  provider: Optional[str] = None,
                  temperature: float = 0.0) -> BaseLanguageModel:
        """
        Get LLM model with automatic fallback
        
        Args:
            provider: Preferred provider ("openai" or "huggingface")
            temperature: Model temperature
            
        Returns:
            BaseLanguageModel instance
            
        Raises:
            ValueError: If no provider is available
        """
        # Try preferred provider first
        if provider == "openai" or (provider is None and self.primary_provider == "openai"):
            model = self.get_openai_model(temperature)
            if model:
                return model
        
        if provider == "huggingface" or (provider is None and self.primary_provider == "huggingface"):
            model = self.get_huggingface_model(temperature)
            if model:
                return model
        
        # Try fallback
        if provider != "openai":
            model = self.get_openai_model(temperature)
            if model:
                print("Using OpenAI as fallback")
                return model
        
        if provider != "huggingface":
            model = self.get_huggingface_model(temperature)
            if model:
                print("Using Hugging Face as fallback")
                return model
        
        raise ValueError("No LLM provider is configured. Please set OPENAI_API_KEY or HUGGINGFACE_API_KEY.")
    
    def is_available(self, provider: str) -> bool:
        """Check if a provider is available"""
        if provider == "openai":
            return bool(settings.OPENAI_API_KEY)
        elif provider == "huggingface":
            return bool(settings.HUGGINGFACE_API_KEY)
        return False


# Global provider instance
llm_provider = LLMProvider()

