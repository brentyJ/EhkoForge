"""
OpenAI API provider implementation.

Uses the official OpenAI Python SDK.
Install: pip install openai
"""

from typing import Optional

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .base import LLMProvider, LLMResponse


class OpenAIProvider(LLMProvider):
    """
    OpenAI API provider via official SDK.
    
    Requires: pip install openai
    
    Models:
        - gpt-4o-mini: Cost-effective, good for processing tasks
        - gpt-4o: Higher quality, more expensive
        - gpt-4.1: Future model (when available)
    """
    
    PROVIDER_NAME = "openai"
    
    def __init__(self, api_key: str, model: Optional[str] = None):
        """
        Initialise OpenAI provider.
        
        Args:
            api_key: OpenAI API key.
            model: Model override. Defaults to gpt-4o-mini.
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "openai package not installed. Run: pip install openai"
            )
        
        super().__init__(api_key, model)
        self.client = openai.OpenAI(api_key=api_key)
    
    @property
    def default_model(self) -> str:
        """Default to GPT-4o-mini for cost-effective processing."""
        return "gpt-4o-mini"
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Generate response from OpenAI.
        
        Args:
            prompt: User message.
            system_prompt: System instructions for behaviour.
            max_tokens: Maximum response tokens.
            temperature: Creativity (0.0-2.0 for OpenAI).
        
        Returns:
            LLMResponse with content or error.
        """
        try:
            # Build messages array
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            # API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            # Extract content
            content = ""
            if response.choices:
                content = response.choices[0].message.content or ""
            
            # Token usage
            input_tokens = 0
            output_tokens = 0
            if response.usage:
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens
            
            return LLMResponse(
                content=content,
                model=self.model,
                provider=self.PROVIDER_NAME,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                raw_response=response.model_dump() if hasattr(response, "model_dump") else None,
            )
            
        except openai.AuthenticationError as e:
            return LLMResponse(
                content="",
                model=self.model,
                provider=self.PROVIDER_NAME,
                error=f"Authentication failed: {e}",
            )
        except openai.RateLimitError as e:
            return LLMResponse(
                content="",
                model=self.model,
                provider=self.PROVIDER_NAME,
                error=f"Rate limit exceeded: {e}",
            )
        except openai.APIError as e:
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
            temperature: Creativity (0.0-2.0).
        
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
