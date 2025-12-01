"""
LLM Integration for forge_server.py

This file shows how to integrate the ehkoforge.llm module into the Flask server.
Copy the relevant sections into forge_server.py to enable real LLM responses.

SETUP:
1. pip install anthropic
2. Set environment variable: ANTHROPIC_API_KEY=sk-ant-...
3. Replace generate_ehko_response() in forge_server.py with the version below

"""

# =============================================================================
# ADD THESE IMPORTS TO forge_server.py (after existing imports)
# =============================================================================

import sys
from pathlib import Path

# Add parent directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent))

from ehkoforge.llm import (
    ClaudeProvider,
    EhkoContextBuilder,
    LLMConfig,
    create_default_config,
    get_system_prompt,
)

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
        
        # Get system prompt
        system_prompt = get_system_prompt(
            forger_name="Brent",  # TODO: Make configurable
            conversation_mode="reflective",
        )
        
        # Generate response
        if reflection_context:
            response = provider.generate_with_context(
                prompt=user_message,
                context=reflection_context,
                system_prompt=system_prompt,
                max_tokens=512,
                temperature=0.7,
            )
        else:
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
# ADD THIS NEW API ENDPOINT TO forge_server.py (for testing)
# =============================================================================

@app.route("/api/llm/status", methods=["GET"])
def llm_status():
    """Check LLM provider status."""
    provider = get_llm_provider()
    
    if provider is None:
        return jsonify({
            "status": "offline",
            "provider": None,
            "message": "No LLM provider configured. Using templated responses.",
        })
    
    return jsonify({
        "status": "online",
        "provider": provider.PROVIDER_NAME,
        "model": provider.model,
        "message": "LLM provider active.",
    })


@app.route("/api/llm/test", methods=["POST"])
def llm_test():
    """Test LLM generation with a simple prompt."""
    provider = get_llm_provider()
    
    if provider is None:
        return jsonify({"error": "No LLM provider configured"}), 503
    
    data = request.get_json() or {}
    prompt = data.get("prompt", "Hello, this is a test.")
    
    response = provider.generate(prompt, max_tokens=100)
    
    return jsonify({
        "success": response.success,
        "content": response.content,
        "error": response.error,
        "tokens": {
            "input": response.input_tokens,
            "output": response.output_tokens,
        }
    })


# =============================================================================
# STARTUP ADDITIONS (add to main block)
# =============================================================================

# Add after "init_session_tables()":
#
#     # Test LLM connection
#     provider = get_llm_provider()
#     if provider:
#         print(f"[OK] LLM provider: {provider.PROVIDER_NAME} ({provider.model})")
#     else:
#         print("[WARN] No LLM provider - using templated responses")
