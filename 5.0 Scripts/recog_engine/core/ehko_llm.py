"""
ReCog Core - EhkoForge LLM Wrapper v1.0

Bridges ehkoforge.llm providers to ReCog's LLMProvider interface.
"""

from typing import Optional, Dict

# ReCog interface
from recog_engine.core.llm import LLMProvider as RecogLLMProvider, LLMResponse as RecogLLMResponse

# EhkoForge providers
from ehkoforge.llm import (
    LLMProvider as EhkoLLMProvider,
    get_provider_for_processing,
    create_default_config,
)


class EhkoLLMWrapper(RecogLLMProvider):
    """
    Wraps an ehkoforge.llm provider for use with ReCog engine.
    
    Usage:
        from ehkoforge.llm import get_provider_for_processing, create_default_config
        config = create_default_config(config_path)
        ehko_provider = get_provider_for_processing(config)
        
        recog_provider = EhkoLLMWrapper(ehko_provider)
        # Now use recog_provider with ReCog extractor/correlator/synthesizer
    """
    
    def __init__(self, ehko_provider: EhkoLLMProvider):
        self._provider = ehko_provider
    
    @property
    def name(self) -> str:
        return self._provider.PROVIDER_NAME
    
    @property
    def model(self) -> str:
        return self._provider.model
    
    def generate(self,
                 prompt: str,
                 system_prompt: Optional[str] = None,
                 temperature: float = 0.3,
                 max_tokens: int = 2000) -> RecogLLMResponse:
        """Generate response using wrapped provider."""
        try:
            response = self._provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            if response.success:
                return RecogLLMResponse.success_response(
                    content=response.content,
                    model=response.model,
                    usage={
                        "input_tokens": response.input_tokens,
                        "output_tokens": response.output_tokens,
                    }
                )
            else:
                return RecogLLMResponse.error_response(response.error or "Unknown error")
                
        except Exception as e:
            return RecogLLMResponse.error_response(str(e))
    
    def is_available(self) -> bool:
        """Check if underlying provider is available."""
        return self._provider.test_connection()


def create_recog_provider(config_path=None):
    """
    Create a ReCog-compatible LLM provider from EhkoForge config.
    
    Args:
        config_path: Path to config directory (uses default if None)
        
    Returns:
        EhkoLLMWrapper instance or None if no provider configured
    """
    from pathlib import Path
    
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent.parent / "Config"
    
    config = create_default_config(config_path)
    ehko_provider = get_provider_for_processing(config)
    
    if ehko_provider:
        return EhkoLLMWrapper(ehko_provider)
    return None


__all__ = ["EhkoLLMWrapper", "create_recog_provider"]
