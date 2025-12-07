"""Debug script for extract_docs issue."""
from pathlib import Path
import traceback

print("Testing adapter and scheduler...")

try:
    from recog_engine.adapters.ehkoforge import EhkoForgeAdapter
    
    db = Path('G:/Other computers/Ehko/Obsidian/EhkoForge/_data/ehko_index.db')
    
    print("\n1. Testing adapter directly...")
    adapter = EhkoForgeAdapter(db, run_migrations_on_init=False)
    count = adapter.get_unprocessed_chunk_count()
    print(f"   Unprocessed chunks: {count}")
    
    print("\n2. Testing scheduler...")
    from recog_engine.scheduler import RecogScheduler
    s = RecogScheduler(db)
    
    print("\n3. Testing _check_doc_extraction_needed...")
    result = s._check_doc_extraction_needed()
    print(f"   Result: {result}")
    
    print("\n4. Testing full check_and_queue...")
    ops = s.check_and_queue()
    print(f"   Queued: {ops}")
    
    print("\nAll tests passed!")
    
except Exception as e:
    print(f"\nERROR: {e}")
    traceback.print_exc()
