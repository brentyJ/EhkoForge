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
from .system_prompt import (
    FORGING_MODE_PROMPT,
    VISITOR_MODE_PROMPT,
    ARCHIVED_MODE_PROMPT,
    get_system_prompt,
    get_forging_prompt,
    get_visitor_prompt,
)

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
    # System prompts
    "FORGING_MODE_PROMPT",
    "VISITOR_MODE_PROMPT",
    "ARCHIVED_MODE_PROMPT",
    "get_system_prompt",
    "get_forging_prompt",
    "get_visitor_prompt",
]
