#!/usr/bin/env python3
"""
EhkoForge Reorientation Migration Runner

Applies the reorientation migration:
- Renames ingot tables to insite
- Adds Authority system tables
- Adds Mana system tables

Run: python run_reorientation_migration.py
"""

import sqlite3
from pathlib import Path


# Configuration
EHKOFORGE_ROOT = Path("G:/Other computers/Ehko/Obsidian/EhkoForge")
DATABASE_PATH = EHKOFORGE_ROOT / "_data" / "ehko_index.db"
MIGRATION_PATH = EHKOFORGE_ROOT / "5.0 Scripts" / "migrations" / "reorientation_v0_1.sql"


def run_migration():
    """Execute the reorientation migration."""
    
    print("=" * 60)
    print("EHKOFORGE REORIENTATION MIGRATION")
    print("=" * 60)
    print(f"Database: {DATABASE_PATH}")
    print(f"Migration: {MIGRATION_PATH}")
    print("-" * 60)
    
    # Check files exist
    if not DATABASE_PATH.exists():
        print(f"[ERROR] Database not found: {DATABASE_PATH}")
        return False
    
    if not MIGRATION_PATH.exists():
        print(f"[ERROR] Migration file not found: {MIGRATION_PATH}")
        return False
    
    # Read migration SQL
    with open(MIGRATION_PATH, "r", encoding="utf-8") as f:
        migration_sql = f.read()
    
    # Connect and execute
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()
    
    try:
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Split by semicolons and execute each statement
        # (executescript doesn't give good error messages)
        statements = [s.strip() for s in migration_sql.split(';') if s.strip()]
        
        for i, stmt in enumerate(statements):
            # Skip comments-only statements
            lines = [l for l in stmt.split('\n') if l.strip() and not l.strip().startswith('--')]
            if not lines:
                continue
                
            try:
                cursor.execute(stmt)
                # Print progress for table creation
                if 'CREATE TABLE' in stmt.upper():
                    # Extract table name
                    import re
                    match = re.search(r'CREATE TABLE[^(]*?(\w+)', stmt, re.IGNORECASE)
                    if match:
                        print(f"[OK] Created/verified table: {match.group(1)}")
                elif 'INSERT' in stmt.upper() and 'identity_pillars' in stmt.lower():
                    print(f"[OK] Seeded identity pillars")
                elif 'INSERT' in stmt.upper() and 'mana_costs' in stmt.lower():
                    print(f"[OK] Seeded mana costs")
            except sqlite3.Error as e:
                # Some errors are expected (e.g., column already exists)
                if 'duplicate column' in str(e).lower():
                    pass
                elif 'already exists' in str(e).lower():
                    pass
                else:
                    print(f"[WARN] Statement {i+1}: {e}")
        
        conn.commit()
        print("-" * 60)
        print("[OK] Migration completed successfully")
        
        # Verify key tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            AND name IN ('insites', 'ehko_authority', 'mana_state', 'mana_costs', 'identity_pillars')
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"[OK] Verified tables: {', '.join(tables)}")
        
        # Show initial state
        cursor.execute("SELECT * FROM ehko_authority WHERE id = 1")
        auth_row = cursor.fetchone()
        if auth_row:
            print(f"[OK] Authority initialised: stage={auth_row[7]}, total={auth_row[6]}")
        
        cursor.execute("SELECT * FROM mana_state WHERE id = 1")
        mana_row = cursor.fetchone()
        if mana_row:
            print(f"[OK] Mana initialised: {mana_row[1]}/{mana_row[2]} (regen: {mana_row[3]}/hr)")
        
        cursor.execute("SELECT COUNT(*) FROM identity_pillars")
        pillar_count = cursor.fetchone()[0]
        print(f"[OK] Identity pillars: {pillar_count}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"[ERROR] Migration failed: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


def verify_migration():
    """Verify migration was applied correctly."""
    
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()
    
    try:
        # Check all expected tables
        expected_tables = [
            'insites', 'insite_sources', 'insite_history',
            'ehko_authority', 'identity_pillars',
            'mana_state', 'mana_costs', 'mana_transactions'
        ]
        
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table'
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        all_present = True
        for table in expected_tables:
            if table in existing_tables:
                print(f"[OK] {table}")
            else:
                print(f"[MISSING] {table}")
                all_present = False
        
        # Check data migration from ingots to insites
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='ingots'")
        if cursor.fetchone()[0]:
            cursor.execute("SELECT COUNT(*) FROM ingots")
            old_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM insites")
            new_count = cursor.fetchone()[0]
            print(f"\n[DATA] Ingots: {old_count} -> Insites: {new_count}")
        
        return all_present
        
    finally:
        conn.close()


if __name__ == "__main__":
    success = run_migration()
    if success:
        verify_migration()
    print("\n" + "=" * 60)
