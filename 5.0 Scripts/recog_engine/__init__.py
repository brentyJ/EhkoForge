"""
ReCog Engine - Recursive Cognition Engine v0.2
Licensed under AGPLv3 - See LICENSE in this directory

Commercial licenses available: brent@ehkolabs.io

v0.2 Changes:
- Added Authority system (Ehko advancement)
- Added Mana system (resource economy)
- Stage-based personality dampener
"""

from .tier0 import Tier0Processor, preprocess_text, summarise_for_prompt
from .smelt import SmeltProcessor, queue_for_smelt, get_queue_stats, should_auto_smelt
from .prompts import (
    get_system_prompt, 
    get_forging_prompt, 
    get_visitor_prompt,
    get_stage_for_authority,
)
from .authority_mana import (
    # Authority
    calculate_authority_components,
    calculate_total_authority,
    update_authority,
    get_current_authority,
    # Mana
    get_mana_state,
    get_mana_cost,
    spend_mana,
    check_mana_available,
    get_dormant_response,
    set_mana_config,
    refill_mana,
)

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
    'get_stage_for_authority',
    # Authority
    'calculate_authority_components',
    'calculate_total_authority',
    'update_authority',
    'get_current_authority',
    # Mana
    'get_mana_state',
    'get_mana_cost',
    'spend_mana',
    'check_mana_available',
    'get_dormant_response',
    'set_mana_config',
    'refill_mana',
]

__version__ = '0.2.0'
