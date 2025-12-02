"""
Provider factory for LLM instantiation.

Centralises provider creation and role-based model routing.
Allows seamless switching between providers for different use cases.
"""

import logging
from typing import Optional, Type

from .base import LLMProvider
from .claude_provider import ClaudeProvider, ANTHROPIC_AVAILABLE
from .openai_provider import OpenAIProvider, OPENAI_AVAILABLE
from .config import LLMConfig

logger = logging.getLogger(__name__)


class ProviderFactory:
    """
    Factory for creating LLM provider instances.
    
    Supports role-based provider selection:
        - processing: Smelt, tier operations (cost-optimised)
        - conversation: Chat responses (quality-optimised)
        - ehko: Ehko personality generation (customisable)
    """
    
    # Registry of available providers
    _providers: dict[str, Type[LLMProvider]] = {
        "claude": ClaudeProvider,
        "openai": OpenAIProvider,
        # "gemini": GeminiProvider,  # Future
    }
    
    # Provider availability flags
    _availability: dict[str, bool] = {
        "claude": ANTHROPIC_AVAILABLE,
        "openai": OPENAI_AVAILABLE,
        # "gemini": GEMINI_AVAILABLE,  # Future
    }
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[LLMProvider], available: bool = True) -> None:
        """
        Register a new provider type.
        
        Args:
            name: Provider identifier.
            provider_class: LLMProvider subclass.
            available: Whether required package is installed.
        """
        cls._providers[name] = provider_class
        cls._availability[name] = available
        logger.info(f"Registered provider: {name} (available: {available})")
    
    @classmethod
    def get_provider(cls, name: str, config: LLMConfig, model: Optional[str] = None) -> Optional[LLMProvider]:
        """
        Get provider instance by name.
        
        Args:
            name: Provider name ('claude', 'openai', etc.)
            config: LLM configuration with API keys.
            model: Optional model override.
        
        Returns:
            LLMProvider instance or None if unavailable.
        """
        # Check if provider is registered
        if name not in cls._providers:
            logger.error(f"Unknown provider: {name}")
            return None
        
        # Check if package is available
        if not cls._availability.get(name, False):
            logger.warning(f"Provider {name} package not installed")
            return None
        
        # Get provider config
        provider_config = config.get_provider(name)
        if not provider_config or not provider_config.api_key:
            logger.warning(f"No API key configured for provider: {name}")
            return None
        
        # Instantiate provider
        try:
            provider_class = cls._providers[name]
            return provider_class(
                api_key=provider_config.api_key,
                model=model or provider_config.model,
            )
        except Exception as e:
            logger.error(f"Failed to create provider {name}: {e}")
            return None
    
    @classmethod
    def get_for_role(cls, role: str, config: LLMConfig) -> Optional[LLMProvider]:
        """
        Get provider configured for a specific role.
        
        Roles:
            - processing: Smelt, tier ops, batch jobs (cost-optimised)
            - conversation: Chat responses (quality-optimised)
            - ehko: Ehko personality (customisable)
        
        Args:
            role: Role identifier.
            config: LLM configuration.
        
        Returns:
            LLMProvider instance or None if unavailable.
        """
        # Get role-specific provider and model
        if role == "processing":
            provider_name = config.processing_provider
            model = config.processing_model
        elif role == "conversation":
            provider_name = config.conversation_provider
            model = config.conversation_model
        elif role == "ehko":
            provider_name = config.ehko_provider
            model = config.ehko_model
        else:
            logger.warning(f"Unknown role: {role}, using default provider")
            provider_name = config.default_provider
            model = None
        
        # Get the provider
        provider = cls.get_provider(provider_name, config, model)
        
        if provider:
            logger.info(f"Created {provider_name} provider for role '{role}' with model {provider.model}")
        else:
            # Try fallback chain
            logger.warning(f"Primary provider {provider_name} unavailable for role '{role}', trying fallbacks")
            provider = cls.get_fallback(config)
        
        return provider
    
    @classmethod
    def get_fallback(cls, config: LLMConfig) -> Optional[LLMProvider]:
        """
        Get first available provider from fallback chain.
        
        Args:
            config: LLM configuration.
        
        Returns:
            LLMProvider instance or None if all unavailable.
        """
        for provider_config in config.get_fallback_chain():
            provider = cls.get_provider(provider_config.name, config)
            if provider:
                logger.info(f"Using fallback provider: {provider_config.name}")
                return provider
        
        logger.error("No providers available")
        return None
    
    @classmethod
    def list_available(cls) -> list[str]:
        """List all available (installed) providers."""
        return [name for name, available in cls._availability.items() if available]
    
    @classmethod
    def list_configured(cls, config: LLMConfig) -> list[str]:
        """List all configured (with API keys) providers."""
        return [
            name for name in cls._providers.keys()
            if config.get_provider(name) and config.get_provider(name).api_key
        ]


def get_provider_for_processing(config: LLMConfig) -> Optional[LLMProvider]:
    """Convenience function for processing tasks (smelt, tier ops)."""
    return ProviderFactory.get_for_role("processing", config)


def get_provider_for_conversation(config: LLMConfig) -> Optional[LLMProvider]:
    """Convenience function for chat conversations."""
    return ProviderFactory.get_for_role("conversation", config)


def get_provider_for_ehko(config: LLMConfig) -> Optional[LLMProvider]:
    """Convenience function for Ehko personality generation."""
    return ProviderFactory.get_for_role("ehko", config)
