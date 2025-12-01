"""
EhkoForge - Digital identity preservation framework.

Modules:
    llm: LLM provider integrations (Claude, etc.)
    preprocessing: Tier 0 signal extraction
    processing: Smelt processor for ingot extraction
"""

__version__ = "0.2.0"

# Expose key functions at package level for convenience
from ehkoforge.preprocessing import preprocess_text, summarise_for_prompt
from ehkoforge.processing import SmeltProcessor, queue_for_smelt, get_queue_stats, should_auto_smelt
