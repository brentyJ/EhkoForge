#!/usr/bin/env python3
"""
Run document ingestion migration.

Creates tables for bulk document processing.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "_data" / "ehko_index.db"
MIGRATION_PATH = Path(__file__).parent / "migrations" / "document_ingestion_v0_1.sql"


def run_migration():
    """Apply document ingestion migration."""
    print(f"Database: {DB_PATH}")
    print(f"Migration: {MIGRATION_PATH}")
    print()
    
    if not DB_PATH.exists():
        print("ERROR: Database not found")
        return False
    
    if not MIGRATION_PATH.exists():
        print("ERROR: Migration file not found")
        return False
    
    # Read migration
    migration_sql = MIGRATION_PATH.read_text()
    
    # Connect and execute
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        cursor.executescript(migration_sql)
        conn.commit()
        print("✓ Migration applied successfully")
        
        # Verify tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'ingested%' OR name LIKE 'document%' OR name LIKE 'entity%' OR name = 'ingestion_log'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\nCreated tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  - {table}: {count} rows")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
