#!/usr/bin/env python3
"""Fix theme extraction to match single # headers"""

import re
from pathlib import Path

script_path = Path(__file__).parent / "ehko_refresh.py"
content = script_path.read_text(encoding="utf-8")

# Fix the theme extraction regex - change ## to # for theme titles
old = '''        # Extract each themed section
        for theme_match in re.finditer(
            r"^##\\s+(.+?)\\n((?:^-.+?\\n?)+)",
            themes_text,
            re.MULTILINE
        ):'''

new = '''        # Extract each themed section
        for theme_match in re.finditer(
            r"^#\\s+(.+?)\\n((?:^-.+?\\n?)+)",
            themes_text,
            re.MULTILINE
        ):'''

content = content.replace(old, new)

script_path.write_text(content, encoding="utf-8")
print("Fixed theme header detection (changed ## to #)")
