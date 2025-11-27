#!/usr/bin/env python3
"""Quick patch to fix the regex issue in ehko_refresh.py"""

import re
from pathlib import Path

script_path = Path(__file__).parent / "ehko_refresh.py"

# Read the file
content = script_path.read_text(encoding="utf-8")

# Old problematic regex pattern
old_pattern = '''    # Extract themed sections (## Heading with bullets)
    # Look for ## Heading followed by bullet points, before ## Transcriptions
    themes_section = re.search(
        r"(?<=\\n##\\s+Long Summary.+?)^(##.+?)(?=\\n##\\s+Transcriptions|\\Z)",
        content,
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    if themes_section:
        themes_text = themes_section.group(1)
        # Extract each themed section
        for theme_match in re.finditer(
            r"^##\\s+(.+?)\\n((?:^-.+?\\n?)+)",
            themes_text,
            re.MULTILINE
        ):
            theme_title = theme_match.group(1).strip()
            theme_bullets = theme_match.group(2).strip()
            data["themes"].append({
                "title": theme_title,
                "content": theme_bullets
            })'''

# New fixed pattern
new_pattern = '''    # Extract themed sections (## Heading with bullets)
    # Find content between Long Summary and Transcriptions
    long_summary_end = re.search(r"^##\\s+Long Summary\\s*\\n.+?(?=\\n##)", content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    transcriptions_start = re.search(r"^##\\s+Transcriptions", content, re.MULTILINE | re.IGNORECASE)
    
    if long_summary_end and transcriptions_start:
        # Get the text between Long Summary section and Transcriptions section
        start_pos = long_summary_end.end()
        end_pos = transcriptions_start.start()
        themes_text = content[start_pos:end_pos]
        
        # Extract each themed section
        for theme_match in re.finditer(
            r"^##\\s+(.+?)\\n((?:^-.+?\\n?)+)",
            themes_text,
            re.MULTILINE
        ):
            theme_title = theme_match.group(1).strip()
            theme_bullets = theme_match.group(2).strip()
            data["themes"].append({
                "title": theme_title,
                "content": theme_bullets
            })'''

# Replace
content = content.replace(old_pattern, new_pattern)

# Write back
script_path.write_text(content, encoding="utf-8")

print("Fixed regex in ehko_refresh.py")
