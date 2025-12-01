"""
Claude API provider implementation.

Uses the official Anthropic Python SDK.
Install: pip install anthropic
"""

from typing import Optional

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from .base import LLMProvider, LLMResponse


class ClaudeProvider(LLMProvider):
    """
    Claude API provider via Anthropic SDK.
    
    Requires: pip install anthropic
    """
    
    PROVIDER_NAME = "claude"
    
    def __init__(self, api_key: str, model: Optional[str] = None):
        """
        Initialise Claude provider.
        
        Args:
            api_key: Anthropic API key.
            model: Model override. Defaults to claude-sonnet-4-20250514.
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "anthropic package not installed. Run: pip install anthropic"
            )
        
        super().__init__(api_key, model)
        self.client = anthropic.Anthropic(api_key=api_key)
    
    @property
    def default_model(self) -> str:
        """Default to Claude Sonnet 4 for balance of quality and cost."""
        return "claude-sonnet-4-20250514"
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Generate response from Claude.
        
        Args:
            prompt: User message.
            system_prompt: System instructions for Ehko behaviour.
            max_tokens: Maximum response tokens.
            temperature: Creativity (0.0-1.0).
        
        Returns:
            LLMResponse with content or error.
        """
        try:
            # Build message payload
            messages = [{"role": "user", "content": prompt}]
            
            # API call
            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": messages,
            }
            
            if system_prompt:
                kwargs["system"] = system_prompt
            
            if temperature is not None:
                kwargs["temperature"] = temperature
            
            response = self.client.messages.create(**kwargs)
            
            # Extract content
            content = ""
            if response.content:
                content = response.content[0].text
            
            return LLMResponse(
                content=content,
                model=self.model,
                provider=self.PROVIDER_NAME,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                raw_response=response.model_dump() if hasattr(response, "model_dump") else None,
            )
            
        except anthropic.AuthenticationError as e:
            return LLMResponse(
                content="",
                model=self.model,
                provider=self.PROVIDER_NAME,
                error=f"Authentication failed: {e}",
            )
        except anthropic.RateLimitError as e:
            return LLMResponse(
                content="",
                model=self.model,
                provider=self.PROVIDER_NAME,
                error=f"Rate limit exceeded: {e}",
            )
        except anthropic.APIError as e:
            return LLMResponse(
                content="",
                model=self.model,
                provider=self.PROVIDER_NAME,
                error=f"API error: {e}",
            )
        except Exception as e:
            return LLMResponse(
                content="",
                model=self.model,
                provider=self.PROVIDER_NAME,
                error=f"Unexpected error: {e}",
            )
    
    def generate_with_context(
        self,
        prompt: str,
        context: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Generate response with reflection context injected.
        
        Context is prepended to the system prompt as reference material.
        
        Args:
            prompt: User message.
            context: Relevant reflections/memories.
            system_prompt: Base system instructions.
            max_tokens: Maximum response tokens.
            temperature: Creativity (0.0-1.0).
        
        Returns:
            LLMResponse with content or error.
        """
        # Build augmented system prompt with context
        context_block = f"""<ehko_context>
The following are relevant reflections and memories from the Forger's vault.
Use these to inform your responses, but do not quote them verbatim.
Speak about the Forger, not as the Forger.

{context}
</ehko_context>"""
        
        if system_prompt:
            augmented_system = f"{system_prompt}\n\n{context_block}"
        else:
            augmented_system = context_block
        
        return self.generate(
            prompt=prompt,
            system_prompt=augmented_system,
            max_tokens=max_tokens,
            temperature=temperature,
        )
