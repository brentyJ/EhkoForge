"""
EhkoForge Processing Module

Smelt processor and queue management for ingot extraction.
"""

from .smelt import (
    SmeltProcessor,
    queue_for_smelt,
    get_queue_stats,
    should_auto_smelt,
)

__all__ = [
    "SmeltProcessor",
    "queue_for_smelt",
    "get_queue_stats",
    "should_auto_smelt",
]
