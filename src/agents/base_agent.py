"""Base agent class for all CardIQ agents - updated for Gemini"""
from abc import ABC, abstractmethod
from typing import Any
from src.api.gemini_client import GeminiClient

class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, gemini_client: GeminiClient = None):
        """Initialize agent with Gemini client"""
        self.claude_client = gemini_client or GeminiClient()  # Keep attr name for compatibility
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """Process input and return output"""
        pass
    
    def _call_llm(self, user_message: str, use_sonnet: bool = False, max_tokens: int = 2000) -> str:
        """Call Gemini API - use_sonnet flag kept for compatibility but uses same model"""
        system_prompt = self.get_system_prompt()
        
        if use_sonnet:
            return self.claude_client.call_sonnet(
                system_prompt=system_prompt,
                user_message=user_message,
                max_tokens=max_tokens
            )
        else:
            return self.claude_client.call_haiku(
                system_prompt=system_prompt,
                user_message=user_message,
                max_tokens=max_tokens
            )