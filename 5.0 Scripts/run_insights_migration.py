#!/usr/bin/env python3
"""
Run insights columns migration.
Adds flagged, reviewed, rejected, and user_context columns to ingots table.
"""

import sqlite3
from pathlib import Path


def run_migration():
    """Apply the insights columns migration."""
    db_path = Path(__file__).parent.parent / "_data" / "ehko_index.db"
    migration_path = Path(__file__).parent / "migrations" / "insights_columns_v0_1.sql"
    
    print(f"Database: {db_path}")
    print(f"Migration: {migration_path}")
    
    if not db_path.exists():
        print("ERROR: Database not found!")
        return False
    
    if not migration_path.exists():
        print("ERROR: Migration file not found!")
        return False
    
    # Read migration SQL
    with open(migration_path, 'r') as f:
        sql = f.read()
    
    # Connect and apply
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if already applied
    cursor.execute("PRAGMA table_info(ingots)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'flagged' in columns:
        print("Migration already applied (flagged column exists)")
        conn.close()
        return True
    
    print("Applying migration...")
    
    try:
        # Execute each ALTER statement separately (SQLite limitation)
        statements = [
            "ALTER TABLE ingots ADD COLUMN flagged INTEGER DEFAULT 0",
            "ALTER TABLE ingots ADD COLUMN flagged_at TEXT",
            "ALTER TABLE ingots ADD COLUMN reviewed INTEGER DEFAULT 0",
            "ALTER TABLE ingots ADD COLUMN reviewed_at TEXT",
            "ALTER TABLE ingots ADD COLUMN rejected INTEGER DEFAULT 0",
            "ALTER TABLE ingots ADD COLUMN rejected_at TEXT",
            "ALTER TABLE ingots ADD COLUMN user_context TEXT",
            "CREATE INDEX IF NOT EXISTS idx_ingots_flagged ON ingots(flagged) WHERE flagged = 1",
            "CREATE INDEX IF NOT EXISTS idx_ingots_reviewed ON ingots(reviewed)",
        ]
        
        for stmt in statements:
            try:
                cursor.execute(stmt)
                print(f"  ✓ {stmt[:60]}...")
            except sqlite3.OperationalError as e:
                if "duplicate column" in str(e).lower():
                    print(f"  - Skipped (already exists): {stmt[:40]}...")
                else:
                    raise
        
        conn.commit()
        print("\nMigration applied successfully!")
        
        # Verify
        cursor.execute("PRAGMA table_info(ingots)")
        new_columns = [col[1] for col in cursor.fetchall()]
        added = [c for c in ['flagged', 'flagged_at', 'reviewed', 'reviewed_at', 
                              'rejected', 'rejected_at', 'user_context'] if c in new_columns]
        print(f"Verified columns: {', '.join(added)}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
    
    return True


if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)
