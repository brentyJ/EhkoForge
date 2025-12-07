#!/usr/bin/env python3
"""Quick test of scheduler import and creation."""

from pathlib import Path

DATABASE_PATH = Path("G:/Other computers/Ehko/Obsidian/EhkoForge/_data/ehko_index.db")
EHKOFORGE_ROOT = Path("G:/Other computers/Ehko/Obsidian/EhkoForge")

print("1. Importing RecogScheduler...")
try:
    from recog_engine.scheduler import RecogScheduler
    print("   OK")
except Exception as e:
    print(f"   FAIL: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("2. Creating scheduler instance...")
try:
    scheduler = RecogScheduler(
        db_path=DATABASE_PATH,
        config_path=EHKOFORGE_ROOT / "Config",
    )
    print("   OK")
except Exception as e:
    print(f"   FAIL: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("3. Calling check_and_queue...")
try:
    queued = scheduler.check_and_queue()
    print(f"   OK: {len(queued)} operations queued")
    for op in queued:
        print(f"      - {op}")
except Exception as e:
    print(f"   FAIL: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\nAll tests passed!")
