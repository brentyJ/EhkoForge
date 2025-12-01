"""
Base classes for LLM providers.

All providers inherit from LLMProvider and implement the same interface,
allowing seamless swapping between Claude, ChatGPT, Gemini, or local models.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LLMResponse:
    """Standardised response from any LLM provider."""
    
    content: str
    """The generated text response."""
    
    model: str
    """Model identifier used (e.g., 'claude-sonnet-4-20250514')."""
    
    provider: str
    """Provider name (e.g., 'claude', 'openai', 'gemini')."""
    
    input_tokens: int = 0
    """Token count for input/prompt."""
    
    output_tokens: int = 0
    """Token count for generated response."""
    
    raw_response: Optional[dict] = field(default=None, repr=False)
    """Full API response for debugging."""
    
    error: Optional[str] = None
    """Error message if generation failed."""
    
    @property
    def success(self) -> bool:
        """True if response generated without error."""
        return self.error is None and bool(self.content)
    
    @property
    def total_tokens(self) -> int:
        """Combined input + output tokens."""
        return self.input_tokens + self.output_tokens


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    Implement this interface to add new providers (OpenAI, Gemini, local, etc).
    """
    
    PROVIDER_NAME: str = "base"
    """Identifier for this provider."""
    
    def __init__(self, api_key: str, model: Optional[str] = None):
        """
        Initialise provider with API credentials.
        
        Args:
            api_key: API key for the service.
            model: Optional model override. Uses default if not specified.
        """
        self.api_key = api_key
        self.model = model or self.default_model
    
    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default model identifier for this provider."""
        pass
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: User message/query.
            system_prompt: System instructions (Ehko behaviour rules).
            max_tokens: Maximum response length.
            temperature: Creativity control (0.0 = deterministic, 1.0 = creative).
        
        Returns:
            LLMResponse with generated content or error.
        """
        pass
    
    @abstractmethod
    def generate_with_context(
        self,
        prompt: str,
        context: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Generate response with injected reflection context.
        
        Args:
            prompt: User message/query.
            context: Relevant reflections/memories to inject.
            system_prompt: System instructions.
            max_tokens: Maximum response length.
            temperature: Creativity control.
        
        Returns:
            LLMResponse with generated content or error.
        """
        pass
    
    def test_connection(self) -> bool:
        """
        Verify API key and connectivity.
        
        Returns:
            True if provider is accessible and authenticated.
        """
        try:
            response = self.generate("Hello", max_tokens=10)
            return response.success
        except Exception:
            return False
