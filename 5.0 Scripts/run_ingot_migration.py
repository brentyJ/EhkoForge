#!/usr/bin/env python3
"""
Run Ingot System Migration v0.1

Creates the new tables for the smelt/ingot pipeline.
Safe to run multiple times (uses IF NOT EXISTS).
"""

import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path("G:/Other computers/Ehko/Obsidian/EhkoForge/_data/ehko_index.db")
MIGRATION_PATH = Path("G:/Other computers/Ehko/Obsidian/EhkoForge/5.0 Scripts/migrations/ingot_migration_v0_1.sql")


def run_migration():
    """Execute the migration SQL."""
    print(f"Running migration on: {DB_PATH}")
    print(f"Migration file: {MIGRATION_PATH}")
    print("-" * 50)
    
    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        return False
    
    if not MIGRATION_PATH.exists():
        print(f"ERROR: Migration file not found at {MIGRATION_PATH}")
        return False
    
    # Read migration SQL
    migration_sql = MIGRATION_PATH.read_text(encoding="utf-8")
    
    # Connect and execute
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        cursor.executescript(migration_sql)
        conn.commit()
        print("[OK] Migration executed successfully")
        
        # Verify tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        new_tables = [
            "smelt_queue",
            "transcript_segments",
            "annotations",
            "ingots",
            "ingot_sources",
            "ingot_history",
            "ehko_personality_layers",
        ]
        
        print("\nTable verification:")
        for table in new_tables:
            if table in tables:
                print(f"  [OK] {table}")
            else:
                print(f"  [MISSING] {table}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"[ERROR] Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    success = run_migration()
    print("\n" + "=" * 50)
    if success:
        print("Migration complete. Ingot system tables are ready.")
    else:
        print("Migration failed. Check errors above.")
