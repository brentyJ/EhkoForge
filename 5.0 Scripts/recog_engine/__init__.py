"""
ReCog Engine - Recursive Cognition Engine
Licensed under AGPLv3 - See LICENSE in this directory

Commercial licenses available: brent@ehkolabs.io
"""

from .tier0 import Tier0Processor
from .smelt import SmeltProcessor
from .prompts import get_system_prompt, get_forging_prompt, get_visitor_prompt
from .forge_integration import ForgeIntegration

__all__ = [
    'Tier0Processor',
    'SmeltProcessor', 
    'get_system_prompt',
    'get_forging_prompt',
    'get_visitor_prompt',
    'ForgeIntegration',
]

__version__ = '0.1.0'
