#!/usr/bin/env python3
"""
Run Entity Registry Migration v0.1
Creates tables for preflight context system.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "_data" / "ehko_index.db"
MIGRATION_PATH = Path(__file__).parent / "migrations" / "entity_registry_v0_1.sql"

def run_migration():
    print(f"Database: {DB_PATH}")
    print(f"Migration: {MIGRATION_PATH}")
    
    if not MIGRATION_PATH.exists():
        print(f"ERROR: Migration file not found: {MIGRATION_PATH}")
        return False
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Read and execute migration
    sql = MIGRATION_PATH.read_text(encoding='utf-8')
    
    try:
        cursor.executescript(sql)
        conn.commit()
        print("Migration applied successfully!")
        
        # Verify tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'entity%' OR name LIKE 'preflight%'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables created: {', '.join(tables)}")
        
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
    input("Press Enter to close...")
