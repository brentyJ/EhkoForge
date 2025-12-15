#!/usr/bin/env python3
"""
EhkoForge - Tethers Migration Runner

Applies the tethers schema to ehko_index.db.
Creates tables for direct LLM provider connections (BYOK).

Usage:
    python run_tethers_migration.py
"""

import sqlite3
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
DB_PATH = SCRIPT_DIR.parent / "_data" / "ehko_index.db"
MIGRATION_PATH = SCRIPT_DIR / "migrations" / "tethers_v0_1.sql"


def run_migration():
    """Execute the tethers migration."""
    
    if not DB_PATH.exists():
        print(f"[ERROR] Database not found: {DB_PATH}")
        return False
    
    if not MIGRATION_PATH.exists():
        print(f"[ERROR] Migration file not found: {MIGRATION_PATH}")
        return False
    
    print(f"[TETHERS] Applying migration to: {DB_PATH}")
    
    # Read migration SQL
    with open(MIGRATION_PATH, 'r', encoding='utf-8') as f:
        migration_sql = f.read()
    
    # Connect and execute
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Execute migration (split by semicolons for multiple statements)
        cursor.executescript(migration_sql)
        conn.commit()
        
        # Verify tables created
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'tether%'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view' AND name LIKE 'v_tether%' OR name LIKE 'v_active%'
            ORDER BY name
        """)
        views = [row[0] for row in cursor.fetchall()]
        
        print(f"[TETHERS] Migration complete!")
        print(f"[TETHERS] Tables created: {', '.join(tables)}")
        print(f"[TETHERS] Views created: {', '.join(views)}")
        
        # Show provider seed data
        cursor.execute("SELECT provider_key, display_name FROM tether_providers ORDER BY display_order")
        providers = cursor.fetchall()
        print(f"[TETHERS] Providers seeded: {', '.join(p[0] for p in providers)}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"[ERROR] Migration failed: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)
