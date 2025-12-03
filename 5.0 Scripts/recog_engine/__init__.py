"""
ReCog Engine - Recursive Cognition Engine
Licensed under AGPLv3 - See LICENSE in this directory

Commercial licenses available: brent@ehkolabs.io
"""

from .tier0 import Tier0Processor, preprocess_text, summarise_for_prompt
from .smelt import SmeltProcessor, queue_for_smelt, get_queue_stats, should_auto_smelt
from .prompts import get_system_prompt, get_forging_prompt, get_visitor_prompt

# Note: forge_integration.py is a guide document, not auto-imported.
# Import explicitly if needed: from recog_engine.forge_integration import ForgeIntegration

__all__ = [
    # Tier 0
    'Tier0Processor',
    'preprocess_text',
    'summarise_for_prompt',
    # Smelt
    'SmeltProcessor',
    'queue_for_smelt',
    'get_queue_stats', 
    'should_auto_smelt',
    # Prompts
    'get_system_prompt',
    'get_forging_prompt',
    'get_visitor_prompt',
]

__version__ = '0.1.0'
