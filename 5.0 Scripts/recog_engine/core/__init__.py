"""
ReCog Core - Core Module

Copyright (c) 2025 Brent Lefebure
Licensed under AGPLv3 - See LICENSE in repository root

Core types and processors for the ReCog recursive insight engine.
"""

from .types import (
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
)

from .signal import (
    SignalProcessor,
    process_text,
    process_document,
)


__all__ = [
    # Enums
    "ProcessingStatus",
    "PatternType",
    "SynthesisType",
    # Core types
    "Document",
    "Insight",
    "Pattern",
    "Synthesis",
    # State
    "ProcessingState",
    "Corpus",
    # Signal processing
    "SignalProcessor",
    "process_text",
    "process_document",
]
