"""
Configuration management for LLM providers.

Handles API key storage, loading, and provider selection.
Supports environment variables, config files, and runtime configuration.
Includes role-based model routing for different use cases.
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
    
    Supports multiple providers with automatic fallback and role-based routing.
    
    Roles:
        - processing: Smelt, tier ops, batch jobs (cost-optimised)
        - conversation: Chat responses (quality-optimised)
        - ehko: Ehko personality generation (customisable)
    """
    
    providers: dict[str, ProviderConfig] = field(default_factory=dict)
    """Provider configurations keyed by name."""
    
    default_provider: str = "claude"
    """Default provider to use."""
    
    max_tokens: int = 1024
    """Default max tokens for responses."""
    
    temperature: float = 0.7
    """Default temperature for generation."""
    
    # Role-based provider routing
    processing_provider: str = "openai"
    """Provider for processing tasks (smelt, tier ops). Cost-optimised."""
    
    processing_model: str = "gpt-4o-mini"
    """Model for processing tasks. GPT-4o-mini recommended for cost."""
    
    conversation_provider: str = "claude"
    """Provider for chat conversations. Quality-optimised."""
    
    conversation_model: str = "claude-sonnet-4-20250514"
    """Model for conversations. Claude Sonnet recommended for quality."""
    
    ehko_provider: str = "claude"
    """Provider for Ehko personality generation. Customisable by user."""
    
    ehko_model: str = "claude-sonnet-4-20250514"
    """Model for Ehko personality. User-selectable in future."""
    
    @classmethod
    def from_env(cls) -> "LLMConfig":
        """
        Load configuration from environment variables.
        
        Provider keys:
            - ANTHROPIC_API_KEY / CLAUDE_API_KEY
            - OPENAI_API_KEY
            - GEMINI_API_KEY / GOOGLE_API_KEY
        
        Global settings:
            - EHKO_DEFAULT_PROVIDER
            - EHKO_MAX_TOKENS
            - EHKO_TEMPERATURE
        
        Role-based settings:
            - EHKO_PROCESSING_PROVIDER
            - EHKO_PROCESSING_MODEL
            - EHKO_CONVERSATION_PROVIDER
            - EHKO_CONVERSATION_MODEL
            - EHKO_EHKO_PROVIDER (Ehko personality provider)
            - EHKO_EHKO_MODEL (Ehko personality model)
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
        
        # Role-based settings
        config.processing_provider = os.environ.get("EHKO_PROCESSING_PROVIDER", "openai")
        config.processing_model = os.environ.get("EHKO_PROCESSING_MODEL", "gpt-4o-mini")
        
        config.conversation_provider = os.environ.get("EHKO_CONVERSATION_PROVIDER", "claude")
        config.conversation_model = os.environ.get("EHKO_CONVERSATION_MODEL", "claude-sonnet-4-20250514")
        
        config.ehko_provider = os.environ.get("EHKO_EHKO_PROVIDER", "claude")
        config.ehko_model = os.environ.get("EHKO_EHKO_MODEL", "claude-sonnet-4-20250514")
        
        # Fallback: If OpenAI not available for processing, use Claude
        if config.processing_provider == "openai" and "openai" not in config.providers:
            config.processing_provider = "claude"
            config.processing_model = "claude-sonnet-4-20250514"
        
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
            "processing_provider": "openai",
            "processing_model": "gpt-4o-mini",
            "conversation_provider": "claude",
            "conversation_model": "claude-sonnet-4-20250514",
            "ehko_provider": "claude",
            "ehko_model": "claude-sonnet-4-20250514",
            "providers": {
                "claude": {
                    "api_key": "sk-ant-...",
                    "model": "claude-sonnet-4-20250514",
                    "enabled": true,
                    "priority": 0
                },
                "openai": {
                    "api_key": "sk-...",
                    "model": "gpt-4o-mini",
                    "enabled": true,
                    "priority": 1
                }
            }
        }
        """
        config = cls()
        
        if not config_path.exists():
            return config
        
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Global settings
        config.default_provider = data.get("default_provider", "claude")
        config.max_tokens = data.get("max_tokens", 1024)
        config.temperature = data.get("temperature", 0.7)
        
        # Role-based settings
        config.processing_provider = data.get("processing_provider", "openai")
        config.processing_model = data.get("processing_model", "gpt-4o-mini")
        config.conversation_provider = data.get("conversation_provider", "claude")
        config.conversation_model = data.get("conversation_model", "claude-sonnet-4-20250514")
        config.ehko_provider = data.get("ehko_provider", "claude")
        config.ehko_model = data.get("ehko_model", "claude-sonnet-4-20250514")
        
        # Provider configs
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
            "processing_provider": self.processing_provider,
            "processing_model": self.processing_model,
            "conversation_provider": self.conversation_provider,
            "conversation_model": self.conversation_model,
            "ehko_provider": self.ehko_provider,
            "ehko_model": self.ehko_model,
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
    
    def set_role_provider(self, role: str, provider: str, model: Optional[str] = None) -> bool:
        """
        Set provider and model for a specific role.
        
        Args:
            role: Role name ('processing', 'conversation', 'ehko')
            provider: Provider name
            model: Optional model override
        
        Returns:
            True if role was updated.
        """
        if role == "processing":
            self.processing_provider = provider
            if model:
                self.processing_model = model
        elif role == "conversation":
            self.conversation_provider = provider
            if model:
                self.conversation_model = model
        elif role == "ehko":
            self.ehko_provider = provider
            if model:
                self.ehko_model = model
        else:
            return False
        return True


def create_default_config(config_dir: Path, db_path: Optional[Path] = None) -> LLMConfig:
    """
    Create default configuration with environment variable fallbacks.
    
    Checks:
    1. Config file at config_dir/llm_config.json
    2. Database API keys (if db_path provided)
    3. Environment variables
    4. Returns empty config if nothing found
    
    Priority: Database > Environment > Config File
    """
    config_path = config_dir / "llm_config.json"
    
    # Try file first
    if config_path.exists():
        config = LLMConfig.from_file(config_path)
    else:
        config = LLMConfig()
    
    # Merge with environment variables (env takes precedence over file)
    env_config = LLMConfig.from_env()
    for name, env_provider in env_config.providers.items():
        if env_provider.api_key:
            if name in config.providers:
                config.providers[name].api_key = env_provider.api_key
            else:
                config.providers[name] = env_provider
    
    # Also merge role settings from env if explicitly set
    if os.environ.get("EHKO_PROCESSING_PROVIDER"):
        config.processing_provider = env_config.processing_provider
    if os.environ.get("EHKO_PROCESSING_MODEL"):
        config.processing_model = env_config.processing_model
    if os.environ.get("EHKO_CONVERSATION_PROVIDER"):
        config.conversation_provider = env_config.conversation_provider
    if os.environ.get("EHKO_CONVERSATION_MODEL"):
        config.conversation_model = env_config.conversation_model
    if os.environ.get("EHKO_EHKO_PROVIDER"):
        config.ehko_provider = env_config.ehko_provider
    if os.environ.get("EHKO_EHKO_MODEL"):
        config.ehko_model = env_config.ehko_model
    
    # Database keys take HIGHEST priority (allows runtime configuration via UI)
    if db_path and db_path.exists():
        try:
            from recog_engine.mana_manager import get_api_keys
            db_keys = get_api_keys(db_path)
            
            # Claude key from database
            if db_keys.get('claude'):
                if 'claude' in config.providers:
                    config.providers['claude'].api_key = db_keys['claude']
                else:
                    config.providers['claude'] = ProviderConfig(
                        name='claude',
                        api_key=db_keys['claude'],
                        priority=0,
                    )
            
            # OpenAI key from database
            if db_keys.get('openai'):
                if 'openai' in config.providers:
                    config.providers['openai'].api_key = db_keys['openai']
                else:
                    config.providers['openai'] = ProviderConfig(
                        name='openai',
                        api_key=db_keys['openai'],
                        priority=1,
                    )
        except Exception as e:
            # Database keys unavailable, continue with env/file keys
            print(f"[LLM CONFIG] Could not load database keys: {e}")
    
    return config
