"""
EhkoForge - Digital identity preservation framework.

MIT-licensed core modules:
    llm: LLM provider integrations (Claude, OpenAI, etc.)

Note: Tier 0 preprocessing and Smelt processing have moved to the
recog_engine module (AGPL-licensed). Import from there instead:

    from recog_engine.tier0 import preprocess_text, summarise_for_prompt
    from recog_engine.smelt import SmeltProcessor, queue_for_smelt
    from recog_engine.prompts import get_system_prompt
"""

__version__ = "0.3.0"

# Core exports (MIT)
from ehkoforge.llm import (
    EhkoContextBuilder,
    create_default_config,
    get_provider_for_conversation,
    ProviderFactory,
)

__all__ = [
    "EhkoContextBuilder",
    "create_default_config", 
    "get_provider_for_conversation",
    "ProviderFactory",
]
