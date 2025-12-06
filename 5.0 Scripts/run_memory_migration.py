"""
Memory & Progression Migration Runner

Applies memory_progression_v0_1.sql to create:
- Session memory tier tracking (hot/warm/cold)
- Session summaries table
- Ehko progression tracking (stages)
- ReCog processing log
- ReCog reports table
- ReCog queue table

Usage:
    cd "5.0 Scripts"
    python run_memory_migration.py
"""

import sqlite3
from pathlib import Path


def run_migration():
    """Apply the memory and progression migration."""
    
    # Paths
    script_dir = Path(__file__).parent
    db_path = script_dir.parent / "_data" / "ehko_index.db"
    migration_path = script_dir / "migrations" / "memory_progression_v0_1.sql"
    
    print("=" * 60)
    print("Memory & Progression Migration")
    print("=" * 60)
    print(f"Database: {db_path}")
    print(f"Migration: {migration_path}")
    print()
    
    if not db_path.exists():
        print("✗ Database not found!")
        return False
    
    if not migration_path.exists():
        print("✗ Migration file not found!")
        return False
    
    # Read migration SQL
    migration_sql = migration_path.read_text(encoding="utf-8")
    
    # Connect and apply
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if already applied (look for ehko_progression table)
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='ehko_progression'
        """)
        if cursor.fetchone():
            print("⚠ Migration appears to already be applied (ehko_progression exists)")
            
            # Check for new columns on forge_sessions
            cursor.execute("PRAGMA table_info(forge_sessions)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'memory_tier' in columns:
                print("  memory_tier column exists")
            else:
                print("  Adding memory_tier column...")
                cursor.execute("ALTER TABLE forge_sessions ADD COLUMN memory_tier TEXT DEFAULT 'hot'")
            
            if 'archived_at' in columns:
                print("  archived_at column exists")
            else:
                print("  Adding archived_at column...")
                cursor.execute("ALTER TABLE forge_sessions ADD COLUMN archived_at TEXT")
            
            if 'last_accessed_at' in columns:
                print("  last_accessed_at column exists")
            else:
                print("  Adding last_accessed_at column...")
                cursor.execute("ALTER TABLE forge_sessions ADD COLUMN last_accessed_at TEXT")
            
            conn.commit()
            print("\n✓ Columns verified/added")
        else:
            # Fresh migration
            print("Applying migration...")
            conn.executescript(migration_sql)
            print("✓ Migration applied successfully")
        
        # Verify tables
        print("\nVerifying tables:")
        tables = [
            "session_summaries",
            "ehko_progression", 
            "recog_processing_log",
            "recog_reports",
            "recog_queue",
        ]
        
        for table in tables:
            cursor.execute(f"""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='{table}'
            """)
            if cursor.fetchone():
                print(f"  ✓ {table}")
            else:
                print(f"  ✗ {table} MISSING")
        
        # Check progression singleton
        cursor.execute("SELECT stage, created_at FROM ehko_progression WHERE id = 1")
        row = cursor.fetchone()
        if row:
            print(f"\nEhko Progression: stage='{row[0]}', created={row[1]}")
        
        # Count sessions by tier
        cursor.execute("""
            SELECT memory_tier, COUNT(*) 
            FROM forge_sessions 
            GROUP BY memory_tier
        """)
        tiers = cursor.fetchall()
        if tiers:
            print("\nSession memory tiers:")
            for tier, count in tiers:
                print(f"  {tier or 'NULL'}: {count}")
        
        conn.close()
        print("\n" + "=" * 60)
        print("✅ Migration complete")
        print("=" * 60)
        return True
        
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    run_migration()
