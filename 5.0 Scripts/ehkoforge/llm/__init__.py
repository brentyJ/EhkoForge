"""
EhkoForge LLM integration module.

Provides API-agnostic interface for multiple LLM providers.
Supports Claude (Anthropic), OpenAI, and extensible to other providers.
"""

from .base import LLMProvider, LLMResponse
from .claude_provider import ClaudeProvider
from .openai_provider import OpenAIProvider
from .context_builder import EhkoContextBuilder
from .config import LLMConfig, ProviderConfig, create_default_config
from .provider_factory import (
    ProviderFactory,
    get_provider_for_processing,
    get_provider_for_conversation,
    get_provider_for_ehko,
)
# NOTE: System prompts moved to recog_engine.prompts (AGPL)
# Import from there instead: from recog_engine.prompts import get_system_prompt

__all__ = [
    # Base classes
    "LLMProvider",
    "LLMResponse",
    # Providers
    "ClaudeProvider",
    "OpenAIProvider",
    # Factory
    "ProviderFactory",
    "get_provider_for_processing",
    "get_provider_for_conversation",
    "get_provider_for_ehko",
    # Context
    "EhkoContextBuilder",
    # Config
    "LLMConfig",
    "ProviderConfig",
    "create_default_config",
    # NOTE: System prompts moved to recog_engine.prompts (AGPL)
]
