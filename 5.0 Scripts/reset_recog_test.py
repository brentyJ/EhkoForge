"""
Reset ReCog processing state for re-testing.

This clears:
- Document chunks processing flags
- Ingots created from chunks
- Patterns
- Syntheses/personality layers
- Processing logs
- Queue entries
- Reports

Run from: G:\Other computers\Ehko\Obsidian\EhkoForge\5.0 Scripts
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "_data" / "ehko_index.db"

def reset_recog():
    print(f"Resetting ReCog state in: {DB_PATH}")
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Check current state
    cursor.execute("SELECT COUNT(*) FROM document_chunks WHERE recog_processed = 1")
    processed_chunks = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ingots")
    ingot_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ingot_patterns")
    pattern_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ehko_personality_layers")
    synthesis_count = cursor.fetchone()[0]
    
    print(f"\nCurrent state:")
    print(f"  Processed chunks: {processed_chunks}")
    print(f"  Ingots: {ingot_count}")
    print(f"  Patterns: {pattern_count}")
    print(f"  Syntheses: {synthesis_count}")
    
    confirm = input("\nReset all ReCog data? (y/yes): ")
    if confirm.lower() not in ("y", "yes"):
        print("Aborted.")
        return
    
    # Reset document chunks
    cursor.execute("""
        UPDATE document_chunks SET 
            recog_processed = 0,
            tier0_signals = NULL,
            recog_insight_id = NULL
    """)
    print(f"  Reset {cursor.rowcount} document chunks")
    
    # Clear ingot pattern links first (foreign key)
    cursor.execute("DELETE FROM ingot_pattern_insights")
    print(f"  Cleared pattern-insight links")
    
    # Clear patterns
    cursor.execute("DELETE FROM ingot_patterns")
    print(f"  Cleared patterns")
    
    # Clear ingot sources
    cursor.execute("DELETE FROM ingot_sources")
    print(f"  Cleared ingot sources")
    
    # Clear ingots (only those from document chunks)
    cursor.execute("DELETE FROM ingots WHERE recog_insight_id IS NOT NULL")
    print(f"  Cleared {cursor.rowcount} ingots from ReCog")
    
    # Clear personality layers (syntheses)
    cursor.execute("DELETE FROM ehko_personality_layers")
    print(f"  Cleared personality layers")
    
    # Clear processing logs
    cursor.execute("DELETE FROM recog_processing_log")
    print(f"  Cleared processing logs")
    
    # Clear queue
    cursor.execute("DELETE FROM recog_queue")
    print(f"  Cleared queue")
    
    # Clear reports
    cursor.execute("DELETE FROM recog_reports")
    print(f"  Cleared reports")
    
    # Reset document status
    cursor.execute("""
        UPDATE ingested_documents SET 
            status = 'chunked',
            insights_extracted = 0,
            completed_at = NULL
    """)
    print(f"  Reset {cursor.rowcount} documents to 'chunked' status")
    
    conn.commit()
    conn.close()
    
    print("\n✓ ReCog state reset. Ready for re-testing.")
    print("\nNext steps:")
    print("  1. Start forge_server.py")
    print("  2. Go to ReCog tab in UI")
    print("  3. Click 'Check for Work' - should queue extract_docs")
    print("  4. Confirm and process each tier")

if __name__ == "__main__":
    reset_recog()
