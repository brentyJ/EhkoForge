"""
ReCog Engine - Recursive Cognition Engine v1.0

Copyright (c) 2025 Brent Lefebure
Licensed under AGPLv3 - See LICENSE in repository root

Commercial licenses available: brent@ehkolabs.io

ReCog is a standalone text analysis engine that extracts, correlates, 
and synthesises insights from unstructured text corpora.

v1.0 Changes:
- Standalone engine architecture (domain-agnostic)
- Adapter pattern for application integration
- Core types: Document, Insight, Pattern, Synthesis
- Processing tiers: Signal, Extract, Correlate, Synthesise

Legacy v0.x imports still available for backwards compatibility.
"""

__version__ = '1.0.0'


# =============================================================================
# NEW v1.0 CORE API
# =============================================================================

from .core import (
    # Enums
    ProcessingStatus,
    PatternType,
    SynthesisType,
    # Core types
    Document,
    Insight,
    Pattern,
    Synthesis,
    # State
    ProcessingState,
    Corpus,
    # Config
    RecogConfig,
    # LLM interface
    LLMResponse,
    LLMProvider,
    MockLLMProvider,
    # Signal processing (Tier 0)
    SignalProcessor,
    process_text,
    process_document,
    # Extraction (Tier 1)
    Extractor,
    extract_from_text,
    # Correlation (Tier 2)
    Correlator,
    find_patterns,
    # Synthesis (Tier 3)
    Synthesizer,
    synthesise_patterns,
)

from .adapters import (
    RecogAdapter,
    MemoryAdapter,
    EhkoForgeAdapter,
)


# =============================================================================
# LEGACY v0.x API (Backwards Compatibility)
# =============================================================================

# These imports maintain compatibility with existing EhkoForge code.
# They will be deprecated once the EhkoForge adapter is complete.

from .tier0 import (
    Tier0Processor, 
    preprocess_text as legacy_preprocess_text, 
    summarise_for_prompt as legacy_summarise,
)
from .smelt import (
    SmeltProcessor, 
    queue_for_smelt, 
    get_queue_stats, 
    should_auto_smelt,
)
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


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Version
    '__version__',
    
    # === v1.0 Core API ===
    # Enums
    'ProcessingStatus',
    'PatternType',
    'SynthesisType',
    # Core types
    'Document',
    'Insight',
    'Pattern',
    'Synthesis',
    'ProcessingState',
    'Corpus',
    # Config
    'RecogConfig',
    # LLM interface
    'LLMResponse',
    'LLMProvider',
    'MockLLMProvider',
    # Signal processing (Tier 0)
    'SignalProcessor',
    'process_text',
    'process_document',
    # Extraction (Tier 1)
    'Extractor',
    'extract_from_text',
    # Correlation (Tier 2)
    'Correlator',
    'find_patterns',
    # Synthesis (Tier 3)
    'Synthesizer',
    'synthesise_patterns',
    # Adapters
    'RecogAdapter',
    'MemoryAdapter',
    'EhkoForgeAdapter',
    
    # === Legacy v0.x API ===
    # Tier 0
    'Tier0Processor',
    'legacy_preprocess_text',
    'legacy_summarise',
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
