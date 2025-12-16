#!/usr/bin/env python3
"""
Run Entity Registry Migration v0.1
Creates tables for preflight context system.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "_data" / "ehko_index.db"
MIGRATION_PATH = Path(__file__).parent / "migrations" / "entity_registry_v0_1.sql"
MIGRATION_PATH_2 = Path(__file__).parent / "migrations" / "entity_registry_v0_2.sql"

def run_migration():
    print(f"Database: {DB_PATH}")
    print(f"Migration 1: {MIGRATION_PATH}")
    print(f"Migration 2: {MIGRATION_PATH_2}")
    
    if not MIGRATION_PATH.exists():
        print(f"ERROR: Migration file not found: {MIGRATION_PATH}")
        return False
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Read and execute migrations
    sql = MIGRATION_PATH.read_text(encoding='utf-8')
    
    try:
        cursor.executescript(sql)
        print("Migration 1 applied successfully!")
        
        # Run migration 2 if exists
        if MIGRATION_PATH_2.exists():
            sql2 = MIGRATION_PATH_2.read_text(encoding='utf-8')
            try:
                cursor.executescript(sql2)
                print("Migration 2 applied successfully!")
            except Exception as e:
                if "duplicate column" in str(e).lower():
                    print("Migration 2 already applied (column exists)")
                else:
                    print(f"Migration 2 warning: {e}")
        
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
