"""
EhkoForge LLM integration module.

Provides API-agnostic interface for multiple LLM providers.
"""

from .base import LLMProvider, LLMResponse
from .claude_provider import ClaudeProvider
from .context_builder import EhkoContextBuilder
from .config import LLMConfig, ProviderConfig, create_default_config
from .system_prompt import (
    FORGING_MODE_PROMPT,
    VISITOR_MODE_PROMPT,
    ARCHIVED_MODE_PROMPT,
    get_system_prompt,
    get_forging_prompt,
    get_visitor_prompt,
)

__all__ = [
    "LLMProvider",
    "LLMResponse", 
    "ClaudeProvider",
    "EhkoContextBuilder",
    "LLMConfig",
    "ProviderConfig",
    "create_default_config",
    "FORGING_MODE_PROMPT",
    "VISITOR_MODE_PROMPT",
    "ARCHIVED_MODE_PROMPT",
    "get_system_prompt",
    "get_forging_prompt",
    "get_visitor_prompt",
]
