#!/usr/bin/env python3
"""
Run Insights User Interaction Migration v0.1

Adds:
- user_context, flagged, rejected, reviewed columns to ingots
- recog_report_sources table for report drill-down
- v_insights_summary view

Usage:
    python run_insights_migration.py
"""

import sqlite3
from pathlib import Path


def run_migration():
    """Run the insights migration."""
    # Database path
    db_path = Path(__file__).parent.parent / "_data" / "ehko_index.db"
    
    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}")
        return False
    
    # Migration SQL path (same directory)
    sql_path = Path(__file__).parent / "migrations" / "insights_v0_1.sql"
    
    if not sql_path.exists():
        print(f"ERROR: Migration SQL not found at {sql_path}")
        return False
    
    print(f"Database: {db_path}")
    print(f"Migration: {sql_path}")
    print()
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Read and execute migration
    sql = sql_path.read_text()
    
    # Split by statement and execute individually (handles ALTER TABLE errors)
    statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]
    
    applied = 0
    skipped = 0
    
    for stmt in statements:
        if not stmt:
            continue
            
        try:
            cursor.execute(stmt)
            applied += 1
            
            # Extract description from statement
            if 'ALTER TABLE' in stmt:
                parts = stmt.split('ADD COLUMN')
                if len(parts) > 1:
                    col = parts[1].strip().split()[0]
                    print(f"  ✓ Added column: {col}")
            elif 'CREATE TABLE' in stmt:
                name = stmt.split('CREATE TABLE IF NOT EXISTS')[1].strip().split()[0] if 'IF NOT EXISTS' in stmt else stmt.split('CREATE TABLE')[1].strip().split()[0]
                print(f"  ✓ Created table: {name}")
            elif 'CREATE VIEW' in stmt:
                name = stmt.split('CREATE VIEW IF NOT EXISTS')[1].strip().split()[0] if 'IF NOT EXISTS' in stmt else stmt.split('CREATE VIEW')[1].strip().split()[0]
                print(f"  ✓ Created view: {name}")
            elif 'CREATE INDEX' in stmt:
                name = stmt.split('CREATE INDEX IF NOT EXISTS')[1].strip().split()[0] if 'IF NOT EXISTS' in stmt else stmt.split('CREATE INDEX')[1].strip().split()[0]
                print(f"  ✓ Created index: {name}")
                
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e).lower():
                skipped += 1
                print(f"  - Skipped (already exists): {stmt[:50]}...")
            elif 'already exists' in str(e).lower():
                skipped += 1
                print(f"  - Skipped (already exists): {stmt[:50]}...")
            else:
                print(f"  ✗ Error: {e}")
                print(f"    Statement: {stmt[:80]}...")
    
    conn.commit()
    conn.close()
    
    print()
    print(f"Migration complete: {applied} applied, {skipped} skipped")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("INSIGHTS USER INTERACTION MIGRATION v0.1")
    print("=" * 60)
    print()
    
    success = run_migration()
    
    if success:
        print()
        print("Done! Insights tab features ready.")
    else:
        print()
        print("Migration failed.")
        exit(1)
