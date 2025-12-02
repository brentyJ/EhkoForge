"""
ReCog Engine - Forge Server Integration Guide v0.1

Copyright (c) 2025 Brent
Licensed under AGPLv3 - See LICENSE in this directory
Commercial licenses available: brent@ehkolabs.io

This file shows how to integrate the ReCog Engine into forge_server.py.
Copy the relevant sections into forge_server.py to enable real LLM responses.

SETUP:
1. pip install anthropic openai
2. Set environment variables: ANTHROPIC_API_KEY, OPENAI_API_KEY
3. Replace generate_ehko_response() in forge_server.py with the version below

LICENSE NOTE:
This integration code is AGPL-licensed. If you use it in a network service,
you must make your source code available under AGPL or obtain a commercial license.
"""

# =============================================================================
# ADD THESE IMPORTS TO forge_server.py (after existing imports)
# =============================================================================

import sys
from pathlib import Path

# Add parent directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent))

# MIT-licensed infrastructure
from ehkoforge.llm import (
    ClaudeProvider,
    EhkoContextBuilder,
    LLMConfig,
    create_default_config,
)

# AGPL-licensed ReCog components
from recog_engine.prompts import get_system_prompt

# =============================================================================
# ADD THESE GLOBALS TO forge_server.py (after existing config)
# =============================================================================

# LLM Configuration
LLM_CONFIG = create_default_config(EHKOFORGE_ROOT / "Config")
CONTEXT_BUILDER = EhkoContextBuilder(DATABASE_PATH, MIRRORWELL_ROOT)

# Provider instance (lazy init)
_llm_provider = None


def get_llm_provider():
    """Get or create the LLM provider instance."""
    global _llm_provider
    
    if _llm_provider is None:
        provider_config = LLM_CONFIG.get_provider("claude")
        if provider_config and provider_config.api_key:
            try:
                _llm_provider = ClaudeProvider(
                    api_key=provider_config.api_key,
                    model=provider_config.model,
                )
                print(f"[OK] Claude provider initialised: {_llm_provider.model}")
            except ImportError as e:
                print(f"[WARN] Could not initialise Claude provider: {e}")
        else:
            print("[WARN] No Claude API key configured. Using templated responses.")
    
    return _llm_provider


# =============================================================================
# REPLACE generate_ehko_response() IN forge_server.py WITH THIS VERSION
# =============================================================================

def generate_ehko_response(user_message: str, session_context: list = None) -> str:
    """
    Generate an Ehko response to user input.
    
    Uses LLM provider if available, falls back to templates.
    
    Args:
        user_message: The user's message.
        session_context: List of recent messages for context.
    
    Returns:
        Ehko's response string.
    """
    provider = get_llm_provider()
    
    if provider is None:
        # Fallback to templated responses (existing logic)
        return _generate_templated_response(user_message)
    
    try:
        # Build context from reflection corpus
        reflection_context = CONTEXT_BUILDER.build_context(
            query=user_message,
            max_reflections=3,
            max_tokens_estimate=1500,
        )
        
        # Get system prompt (AGPL ReCog component)
        system_prompt = get_system_prompt(
            mode="forging",
            forger_name="Brent",  # TODO: Make configurable
            reflection_context=reflection_context,
        )
        
        # Generate response
        response = provider.generate(
            prompt=user_message,
            system_prompt=system_prompt,
            max_tokens=512,
            temperature=0.7,
        )
        
        if response.success:
            return response.content
        else:
            print(f"[ERROR] LLM error: {response.error}")
            return _generate_templated_response(user_message)
            
    except Exception as e:
        print(f"[ERROR] LLM generation failed: {e}")
        return _generate_templated_response(user_message)


def _generate_templated_response(user_message: str) -> str:
    """
    Original templated response logic (fallback).
    
    Keep this as backup when LLM is unavailable.
    """
    import random
    
    message_lower = user_message.lower()
    
    if any(word in message_lower for word in ["thank", "thanks"]):
        responses = [
            "You're welcome. I'm here whenever you need to reflect.",
            "Of course. Take your time with whatever comes next.",
        ]
    elif any(word in message_lower for word in ["feel", "feeling", "felt"]):
        responses = [
            "Those feelings are worth sitting with. Would you like to explore them further?",
            "I hear you. What do you think is at the root of that feeling?",
            "Thank you for sharing that. Feelings often point to something deeper.",
        ]
    elif any(word in message_lower for word in ["remember", "memory", "memories"]):
        responses = [
            "Memories shape who we are. What made this one surface now?",
            "That memory sounds significant. Would you like to forge it into the vault?",
            "I've noted that. Memories like these often connect to core patterns.",
        ]
    elif any(word in message_lower for word in ["help", "stuck", "confused"]):
        responses = [
            "Let's slow down. What's the smallest piece you can name right now?",
            "Sometimes clarity comes from just getting words out. Keep going.",
            "I'm here. There's no rush to have it all figured out.",
        ]
    elif "?" in user_message:
        responses = [
            "That's a question worth holding. What does your gut tell you?",
            "I wonder what asking that question reveals about where you are right now.",
            "Good question. Let's sit with it rather than rush to an answer.",
        ]
    else:
        responses = [
            "I've noted that. What else is on your mind?",
            "Thank you for sharing. I'm here when you're ready to continue.",
            "That's worth sitting with. Would you like to explore it further?",
            "I hear you. Take whatever time you need.",
            "Noted. These threads often connect to something larger.",
        ]
    
    return random.choice(responses)


# =============================================================================
# FORGE INTEGRATION CLASS (for structured access)
# =============================================================================

class ForgeIntegration:
    """
    Structured integration between ReCog Engine and Forge Server.
    
    Provides clean interface for:
    - Ehko response generation
    - Context building
    - Mode switching
    """
    
    def __init__(self, config_path: Path, db_path: Path, mirrorwell_path: Path):
        """
        Initialise forge integration.
        
        Args:
            config_path: Path to Config directory
            db_path: Path to ehko_index.db
            mirrorwell_path: Path to Mirrorwell vault
        """
        self.config = create_default_config(config_path)
        self.context_builder = EhkoContextBuilder(db_path, mirrorwell_path)
        self._provider = None
        self.current_mode = "forging"
        self.forger_name = "the Forger"
    
    @property
    def provider(self):
        """Lazy-init LLM provider."""
        if self._provider is None:
            provider_config = self.config.get_provider("claude")
            if provider_config and provider_config.api_key:
                self._provider = ClaudeProvider(
                    api_key=provider_config.api_key,
                    model=provider_config.model,
                )
        return self._provider
    
    def generate_response(self, user_message: str, session_context: list = None) -> str:
        """Generate Ehko response with full context."""
        if not self.provider:
            return _generate_templated_response(user_message)
        
        # Build reflection context
        reflection_context = self.context_builder.build_context(
            query=user_message,
            max_reflections=3,
            max_tokens_estimate=1500,
        )
        
        # Get appropriate system prompt
        system_prompt = get_system_prompt(
            mode=self.current_mode,
            forger_name=self.forger_name,
            reflection_context=reflection_context,
        )
        
        # Generate
        response = self.provider.generate(
            prompt=user_message,
            system_prompt=system_prompt,
            max_tokens=512,
            temperature=0.7,
        )
        
        return response.content if response.success else _generate_templated_response(user_message)
    
    def set_mode(self, mode: str, forger_name: str = None):
        """Switch Ehko mode."""
        if mode in ("forging", "visitor", "archived"):
            self.current_mode = mode
        if forger_name:
            self.forger_name = forger_name
    
    def get_status(self) -> dict:
        """Get integration status."""
        return {
            "provider": self.provider.PROVIDER_NAME if self.provider else None,
            "model": self.provider.model if self.provider else None,
            "mode": self.current_mode,
            "forger_name": self.forger_name,
            "active": self.provider is not None,
        }


# =============================================================================
# API ENDPOINTS (add to forge_server.py)
# =============================================================================

# @app.route("/api/llm/status", methods=["GET"])
# def llm_status():
#     """Check LLM provider status."""
#     provider = get_llm_provider()
#     
#     if provider is None:
#         return jsonify({
#             "status": "offline",
#             "provider": None,
#             "message": "No LLM provider configured. Using templated responses.",
#         })
#     
#     return jsonify({
#         "status": "online",
#         "provider": provider.PROVIDER_NAME,
#         "model": provider.model,
#         "message": "LLM provider active.",
#     })


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "ForgeIntegration",
    "get_llm_provider",
    "generate_ehko_response",
]
