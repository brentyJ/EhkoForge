"""
Configuration management for LLM providers.

Handles API key storage, loading, and provider selection.
Supports environment variables, config files, and runtime configuration.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ProviderConfig:
    """Configuration for a single LLM provider."""
    
    name: str
    """Provider identifier (claude, openai, gemini, local)."""
    
    api_key: Optional[str] = None
    """API key for the service."""
    
    model: Optional[str] = None
    """Model override. Uses provider default if not set."""
    
    enabled: bool = True
    """Whether this provider is active."""
    
    priority: int = 0
    """Fallback priority (lower = higher priority)."""


@dataclass  
class LLMConfig:
    """
    Central configuration for all LLM providers.
    
    Supports multiple providers with automatic fallback.
    """
    
    providers: dict[str, ProviderConfig] = field(default_factory=dict)
    """Provider configurations keyed by name."""
    
    default_provider: str = "claude"
    """Default provider to use."""
    
    max_tokens: int = 1024
    """Default max tokens for responses."""
    
    temperature: float = 0.7
    """Default temperature for generation."""
    
    @classmethod
    def from_env(cls) -> "LLMConfig":
        """
        Load configuration from environment variables.
        
        Looks for:
            - ANTHROPIC_API_KEY / CLAUDE_API_KEY
            - OPENAI_API_KEY
            - GEMINI_API_KEY / GOOGLE_API_KEY
            - EHKO_DEFAULT_PROVIDER
            - EHKO_MAX_TOKENS
            - EHKO_TEMPERATURE
        """
        config = cls()
        
        # Claude
        claude_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CLAUDE_API_KEY")
        if claude_key:
            config.providers["claude"] = ProviderConfig(
                name="claude",
                api_key=claude_key,
                priority=0,
            )
        
        # OpenAI
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            config.providers["openai"] = ProviderConfig(
                name="openai",
                api_key=openai_key,
                priority=1,
            )
        
        # Gemini
        gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if gemini_key:
            config.providers["gemini"] = ProviderConfig(
                name="gemini",
                api_key=gemini_key,
                priority=2,
            )
        
        # Global settings
        config.default_provider = os.environ.get("EHKO_DEFAULT_PROVIDER", "claude")
        
        if os.environ.get("EHKO_MAX_TOKENS"):
            config.max_tokens = int(os.environ["EHKO_MAX_TOKENS"])
        
        if os.environ.get("EHKO_TEMPERATURE"):
            config.temperature = float(os.environ["EHKO_TEMPERATURE"])
        
        return config
    
    @classmethod
    def from_file(cls, config_path: Path) -> "LLMConfig":
        """
        Load configuration from JSON file.
        
        Expected format:
        {
            "default_provider": "claude",
            "max_tokens": 1024,
            "temperature": 0.7,
            "providers": {
                "claude": {
                    "api_key": "sk-ant-...",
                    "model": "claude-sonnet-4-20250514",
                    "enabled": true,
                    "priority": 0
                }
            }
        }
        """
        config = cls()
        
        if not config_path.exists():
            return config
        
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        config.default_provider = data.get("default_provider", "claude")
        config.max_tokens = data.get("max_tokens", 1024)
        config.temperature = data.get("temperature", 0.7)
        
        for name, provider_data in data.get("providers", {}).items():
            config.providers[name] = ProviderConfig(
                name=name,
                api_key=provider_data.get("api_key"),
                model=provider_data.get("model"),
                enabled=provider_data.get("enabled", True),
                priority=provider_data.get("priority", 99),
            )
        
        return config
    
    def to_file(self, config_path: Path) -> None:
        """Save configuration to JSON file (excluding API keys for security)."""
        data = {
            "default_provider": self.default_provider,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "providers": {}
        }
        
        for name, provider in self.providers.items():
            data["providers"][name] = {
                "model": provider.model,
                "enabled": provider.enabled,
                "priority": provider.priority,
                # API keys should be set via environment or separate secure storage
                "api_key": "[SET VIA ENVIRONMENT]" if provider.api_key else None,
            }
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    
    def get_provider(self, name: Optional[str] = None) -> Optional[ProviderConfig]:
        """
        Get provider configuration by name.
        
        Args:
            name: Provider name. Uses default if not specified.
        
        Returns:
            ProviderConfig or None if not found.
        """
        name = name or self.default_provider
        return self.providers.get(name)
    
    def get_fallback_chain(self) -> list[ProviderConfig]:
        """
        Get providers sorted by priority for fallback.
        
        Returns:
            List of enabled providers sorted by priority (lowest first).
        """
        enabled = [p for p in self.providers.values() if p.enabled and p.api_key]
        return sorted(enabled, key=lambda p: p.priority)
    
    def add_provider(
        self,
        name: str,
        api_key: str,
        model: Optional[str] = None,
        priority: int = 99,
    ) -> None:
        """Add or update a provider configuration."""
        self.providers[name] = ProviderConfig(
            name=name,
            api_key=api_key,
            model=model,
            enabled=True,
            priority=priority,
        )
    
    def set_api_key(self, provider_name: str, api_key: str) -> bool:
        """
        Set API key for existing provider.
        
        Returns:
            True if provider exists and key was set.
        """
        if provider_name in self.providers:
            self.providers[provider_name].api_key = api_key
            return True
        return False


def create_default_config(config_dir: Path) -> LLMConfig:
    """
    Create default configuration with environment variable fallbacks.
    
    Checks:
    1. Config file at config_dir/llm_config.json
    2. Environment variables
    3. Returns empty config if nothing found
    """
    config_path = config_dir / "llm_config.json"
    
    # Try file first
    if config_path.exists():
        config = LLMConfig.from_file(config_path)
        # Merge with environment variables (env takes precedence for keys)
        env_config = LLMConfig.from_env()
        for name, env_provider in env_config.providers.items():
            if env_provider.api_key:
                if name in config.providers:
                    config.providers[name].api_key = env_provider.api_key
                else:
                    config.providers[name] = env_provider
        return config
    
    # Fall back to environment only
    return LLMConfig.from_env()
