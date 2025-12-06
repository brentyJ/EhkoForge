#!/usr/bin/env python3
"""
Test script for ReCog Scheduler v1.0

Tests the confirmation flow without running actual LLM calls.
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from recog_engine.scheduler import RecogScheduler, OperationType, MANA_COSTS

# Paths
EHKOFORGE_ROOT = Path("G:/Other computers/Ehko/Obsidian/EhkoForge")
DATABASE_PATH = EHKOFORGE_ROOT / "_data" / "ehko_index.db"
CONFIG_PATH = EHKOFORGE_ROOT / "Config"


def main():
    print("=" * 60)
    print("ReCog Scheduler Test")
    print("=" * 60)
    
    # Create scheduler
    scheduler = RecogScheduler(db_path=DATABASE_PATH, config_path=CONFIG_PATH)
    
    # 1. Get initial status
    print("\n[1] Initial Status")
    print("-" * 40)
    status = scheduler.get_status()
    print(f"  Queue: {status['queue']}")
    print(f"  Hot sessions: {status['hot_sessions']}")
    print(f"  Pending insights: {status['pending_insights']}")
    print(f"  Patterns: {status['patterns']}")
    print(f"  LLM available: {status['llm_available']}")
    
    # 2. Run Tier 0 (free signal processing)
    print("\n[2] Running Tier 0 (signal annotation)")
    print("-" * 40)
    tier0_stats = scheduler.run_tier0_automatic()
    print(f"  Sessions processed: {tier0_stats['sessions_processed']}")
    print(f"  Signals extracted: {tier0_stats['signals_extracted']}")
    
    # 3. Check and queue operations
    print("\n[3] Check and Queue Operations")
    print("-" * 40)
    queued = scheduler.check_and_queue()
    if queued:
        for op in queued:
            print(f"  Queued: {op.operation_type}")
            print(f"    {op.description}")
            print(f"    Est. mana: {op.estimated_mana}")
    else:
        print("  No operations queued (nothing to process)")
    
    # 4. Get pending confirmations
    print("\n[4] Pending Confirmations")
    print("-" * 40)
    pending = scheduler.get_pending_confirmations()
    if pending:
        for op in pending:
            print(f"  ID {op.id}: {op.operation_type}")
            print(f"    {op.description}")
            print(f"    Est. mana: {op.estimated_mana}")
            print(f"    Queued: {op.queued_at}")
    else:
        print("  No pending confirmations")
    
    # 5. Show mana costs
    print("\n[5] Mana Costs Reference")
    print("-" * 40)
    for op_type, cost in MANA_COSTS.items():
        print(f"  {op_type.value}: {cost} mana")
    
    # 6. Final status
    print("\n[6] Final Status")
    print("-" * 40)
    status = scheduler.get_status()
    print(f"  Queue: {status['queue']}")
    print(f"  Last processed: {status['last_processed']}")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
    print("\nTo test the full flow via API:")
    print("  1. Start server: python forge_server.py")
    print("  2. Check status: GET /api/recog/status")
    print("  3. Queue ops: POST /api/recog/check")
    print("  4. View pending: GET /api/recog/pending")
    print("  5. Confirm: POST /api/recog/confirm/<id>")
    print("  6. Process: POST /api/recog/process")


if __name__ == "__main__":
    main()
