#!/usr/bin/env python3
"""
Run Mana Purchase System Migration v0.1

Applies database schema changes for mana-core purchasing,
user accounts, API key storage (BYOK), and usage tracking.

Run: python run_mana_migration.py
"""

import sqlite3
from pathlib import Path
from datetime import datetime


EHKOFORGE_ROOT = Path(__file__).parent.parent
DATABASE_PATH = EHKOFORGE_ROOT / "_data" / "ehko_index.db"
MIGRATION_FILE = EHKOFORGE_ROOT / "5.0 Scripts" / "migrations" / "mana_purchase_v0_1.sql"


def run_migration():
    print("=" * 70)
    print("MANA PURCHASE SYSTEM MIGRATION v0.1")
    print("=" * 70)
    print(f"Database: {DATABASE_PATH}")
    print(f"Migration: {MIGRATION_FILE}")
    print("-" * 70)
    
    if not DATABASE_PATH.exists():
        print(f"[ERROR] Database not found: {DATABASE_PATH}")
        return False
    
    if not MIGRATION_FILE.exists():
        print(f"[ERROR] Migration file not found: {MIGRATION_FILE}")
        return False
    
    # Read migration SQL
    with open(MIGRATION_FILE, 'r', encoding='utf-8') as f:
        migration_sql = f.read()
    
    # Connect and execute
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()
    
    try:
        # Execute migration (split by semicolons for multiple statements)
        cursor.executescript(migration_sql)
        conn.commit()
        
        print("[OK] Migration executed successfully")
        print("-" * 70)
        
        # Verify tables created
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN (
                'users', 'user_mana_balance', 'mana_purchases', 
                'user_api_keys', 'user_config', 'mana_usage_log', 
                'mana_pricing'
            )
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"[OK] Created/verified {len(tables)} tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  ✓ {table} ({count} rows)")
        
        # Verify views
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view' AND name LIKE 'v_%'
        """)
        views = [row[0] for row in cursor.fetchall()]
        print(f"\n[OK] Created {len(views)} views:")
        for view in views:
            print(f"  ✓ {view}")
        
        print("-" * 70)
        print("[SUCCESS] Migration complete")
        print("=" * 70)
        
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
