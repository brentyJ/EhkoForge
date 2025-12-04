#!/usr/bin/env python3
"""
Cleanup Script: Remove Unused Route-Based UI Files
Removes incomplete route-based templates and related files that were abandoned
in favor of the single-terminal UI (index.html).

Run: python cleanup_unused_ui.py
"""

import os
from pathlib import Path

EHKOFORGE_ROOT = Path("G:/Other computers/Ehko/Obsidian/EhkoForge")
TEMPLATES_DIR = EHKOFORGE_ROOT / "6.0 Frontend" / "templates"
CSS_DIR = EHKOFORGE_ROOT / "6.0 Frontend" / "static" / "css"
JS_DIR = EHKOFORGE_ROOT / "6.0 Frontend" / "static" / "js"

FILES_TO_DELETE = [
    # Unused templates
    TEMPLATES_DIR / "base.html",
    TEMPLATES_DIR / "reflect.html",
    TEMPLATES_DIR / "forge.html",
    TEMPLATES_DIR / "terminal.html",
    
    # Unused CSS (if any route-specific files exist)
    CSS_DIR / "base.css",
    CSS_DIR / "reflect.css",
    CSS_DIR / "terminal.css",
    
    # Unused JS (if any route-specific files exist)
    JS_DIR / "common.js",
    JS_DIR / "reflect.js",
    JS_DIR / "terminal.js",
]

KEEP_FILES = [
    TEMPLATES_DIR / "index.html",
    CSS_DIR / "main.css",
    JS_DIR / "main.js",
]

def main():
    print("=" * 60)
    print("CLEANUP: Unused Route-Based UI Files")
    print("=" * 60)
    
    deleted_count = 0
    missing_count = 0
    
    for filepath in FILES_TO_DELETE:
        if filepath.exists():
            print(f"[DELETE] {filepath.name}")
            filepath.unlink()
            deleted_count += 1
        else:
            missing_count += 1
    
    print("-" * 60)
    print(f"Deleted: {deleted_count} files")
    print(f"Already missing: {missing_count} files")
    print("-" * 60)
    
    print("\n[VERIFY] Keeping essential files:")
    for filepath in KEEP_FILES:
        status = "✓ EXISTS" if filepath.exists() else "✗ MISSING"
        print(f"  {status} - {filepath.name}")
    
    print("\n[OK] Cleanup complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
