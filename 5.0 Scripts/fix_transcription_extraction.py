#!/usr/bin/env python3
"""Fix transcription section extraction regex"""

import re
from pathlib import Path

script_path = Path(__file__).parent / "ehko_refresh.py"
content = script_path.read_text(encoding="utf-8")

# The issue is that $ with MULTILINE matches end of line, not end of string
# We need \Z to match absolute end of string
old = '''    # Extract transcriptions (timestamped entries)
    transcription_section = re.search(
        r"^##\\s+Transcriptions\\s*\\n(.+?)$",
        content,
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )'''

new = '''    # Extract transcriptions (timestamped entries)
    transcription_section = re.search(
        r"^##\\s+Transcriptions\\s*\\n(.+?)\\Z",
        content,
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )'''

content = content.replace(old, new)

script_path.write_text(content, encoding="utf-8")
print("Fixed transcription section extraction (changed $ to \\Z)")
