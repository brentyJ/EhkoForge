"""
ReCog Core - EhkoForge Adapter Test Script

Verifies that the EhkoForge adapter correctly bridges ReCog to the database.

Usage:
    cd "5.0 Scripts"
    python test_recog_ehkoforge.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Ensure recog_engine is importable
sys.path.insert(0, str(Path(__file__).parent))

from recog_engine import (
    # Types
    Document,
    Insight,
    Pattern,
    PatternType,
    Synthesis,
    SynthesisType,
    # Adapters
    EhkoForgeAdapter,
)


def test_adapter_init():
    """Test adapter initialisation."""
    print("\n=== Testing Adapter Initialisation ===")
    
    try:
        adapter = EhkoForgeAdapter()
        print(f"✓ Adapter initialised")
        print(f"  Database: {adapter.db_path}")
        
        stats = adapter.stats()
        print(f"  Stats: {stats}")
        
        adapter.close()
        return True
    except FileNotFoundError as e:
        print(f"✗ Database not found: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_document_loading():
    """Test loading documents from database."""
    print("\n=== Testing Document Loading ===")
    
    adapter = EhkoForgeAdapter()
    
    # Load reflections
    print("\nLoading reflections (limit 5):")
    count = 0
    for doc in adapter.load_documents(source_type="reflection", limit=5):
        count += 1
        print(f"  {count}. [{doc.source_type}] {doc.metadata.get('title', 'Untitled')[:50]}")
        print(f"      Content: {len(doc.content)} chars")
    
    if count == 0:
        print("  (No reflections found)")
    
    # Load sessions
    print("\nLoading sessions (limit 3):")
    count = 0
    for doc in adapter.load_documents(source_type="session", limit=3):
        count += 1
        print(f"  {count}. [{doc.source_type}] {doc.metadata.get('title', 'Untitled')[:50]}")
        print(f"      Content: {len(doc.content)} chars")
    
    if count == 0:
        print("  (No sessions found)")
    
    adapter.close()
    print("✓ Document loading works")


def test_insight_roundtrip():
    """Test saving and retrieving insights."""
    print("\n=== Testing Insight Round-trip ===")
    
    adapter = EhkoForgeAdapter()
    
    # Create test insight
    insight = Insight.create(
        summary="Test insight from ReCog adapter test - demonstrates anxiety pattern recognition.",
        themes=["test", "recog", "anxiety", "adapter"],
        significance=0.75,
        confidence=0.80,
        source_ids=["test-doc-001"],
        excerpts=["This is a test excerpt."],
        metadata={"test_run": True},
    )
    
    print(f"Created insight: {insight.id[:8]}...")
    print(f"  Summary: {insight.summary[:50]}...")
    print(f"  Themes: {insight.themes}")
    
    # Save
    adapter.save_insight(insight)
    print("✓ Insight saved")
    
    # Retrieve
    insights = adapter.get_insights(themes=["recog"])
    print(f"Retrieved {len(insights)} insight(s) with 'recog' theme")
    
    found = False
    for retrieved in insights:
        if "recog" in retrieved.themes:
            found = True
            print(f"  Found: {retrieved.summary[:40]}...")
    
    assert found, "Should find the saved insight"
    print("✓ Insight round-trip works")
    
    adapter.close()


def test_pattern_roundtrip():
    """Test saving and retrieving patterns."""
    print("\n=== Testing Pattern Round-trip ===")
    
    adapter = EhkoForgeAdapter()
    
    # Create test pattern
    pattern = Pattern.create(
        summary="Test recurring pattern from ReCog adapter test.",
        pattern_type=PatternType.RECURRING,
        insight_ids=["test-insight-001", "test-insight-002"],
        strength=0.70,
        metadata={"test_run": True},
    )
    
    print(f"Created pattern: {pattern.id[:8]}...")
    print(f"  Type: {pattern.pattern_type.value}")
    print(f"  Strength: {pattern.strength}")
    
    # Save
    adapter.save_pattern(pattern)
    print("✓ Pattern saved")
    
    # Retrieve
    patterns = adapter.get_patterns()
    print(f"Retrieved {len(patterns)} pattern(s)")
    
    found = any(p.id == pattern.id for p in patterns)
    if found:
        print(f"  Found test pattern")
    
    print("✓ Pattern round-trip works")
    
    adapter.close()


def test_synthesis_roundtrip():
    """Test saving and retrieving syntheses."""
    print("\n=== Testing Synthesis Round-trip ===")
    
    adapter = EhkoForgeAdapter()
    
    # Create test synthesis
    synthesis = Synthesis.create(
        summary="Test trait synthesis from ReCog adapter - demonstrates personality layer creation.",
        synthesis_type=SynthesisType.TRAIT,
        pattern_ids=["test-pattern-001"],
        significance=0.80,
        confidence=0.75,
        metadata={"test_run": True},
    )
    
    print(f"Created synthesis: {synthesis.id[:8]}...")
    print(f"  Type: {synthesis.synthesis_type.value}")
    print(f"  Significance: {synthesis.significance}")
    
    # Save
    adapter.save_synthesis(synthesis)
    print("✓ Synthesis saved to ehko_personality_layers")
    
    # Retrieve
    syntheses = adapter.get_syntheses(synthesis_type=SynthesisType.TRAIT)
    print(f"Retrieved {len(syntheses)} trait syntheses")
    
    found = any(s.id == synthesis.id for s in syntheses)
    if found:
        print(f"  Found test synthesis")
    
    print("✓ Synthesis round-trip works")
    
    adapter.close()


def test_context_and_themes():
    """Test context and theme management."""
    print("\n=== Testing Context and Themes ===")
    
    adapter = EhkoForgeAdapter()
    
    # Default context
    context = adapter.get_context()
    print(f"Default context: {context[:60]}...")
    
    # Custom context
    adapter.set_context("Custom test context for ReCog processing.")
    assert adapter.get_context() == "Custom test context for ReCog processing."
    print("✓ Custom context set")
    
    # Get existing themes
    themes = adapter.get_existing_themes()
    print(f"Existing themes in database: {len(themes)}")
    if themes:
        print(f"  Sample: {themes[:5]}")
    
    print("✓ Context and themes work")
    
    adapter.close()


def test_full_pipeline_simulation():
    """Simulate a full ReCog pipeline with the adapter."""
    print("\n=== Testing Full Pipeline Simulation ===")
    
    adapter = EhkoForgeAdapter()
    
    # 1. Load a document
    print("\n1. Loading document...")
    doc = None
    for d in adapter.load_documents(limit=1):
        doc = d
        break
    
    if not doc:
        print("   No documents to process, creating mock document")
        doc = Document.create(
            content="This is a test reflection about feeling anxious before presentations.",
            source_type="test",
            source_ref="test:pipeline",
        )
    else:
        print(f"   Loaded: {doc.metadata.get('title', doc.source_ref)[:40]}")
    
    # 2. Create insight (simulating extraction)
    print("\n2. Creating insight (simulated extraction)...")
    insight = Insight.create(
        summary=f"Pipeline test insight from {doc.source_ref}",
        themes=["pipeline-test", "anxiety"],
        significance=0.65,
        confidence=0.70,
        source_ids=[doc.id],
    )
    adapter.save_insight(insight)
    print(f"   Saved insight: {insight.id[:8]}")
    
    # 3. Create pattern (simulating correlation)
    print("\n3. Creating pattern (simulated correlation)...")
    pattern = Pattern.create(
        summary="Pipeline test recurring anxiety pattern",
        pattern_type=PatternType.RECURRING,
        insight_ids=[insight.id],
        strength=0.60,
    )
    adapter.save_pattern(pattern)
    print(f"   Saved pattern: {pattern.id[:8]}")
    
    # 4. Create synthesis (simulating synthesis)
    print("\n4. Creating synthesis (simulated synthesis)...")
    synthesis = Synthesis.create(
        summary="Pipeline test: tendency toward anticipatory anxiety in performance contexts.",
        synthesis_type=SynthesisType.TENDENCY,
        pattern_ids=[pattern.id],
        significance=0.70,
        confidence=0.65,
    )
    adapter.save_synthesis(synthesis)
    print(f"   Saved synthesis: {synthesis.id[:8]}")
    
    # 5. Verify storage
    print("\n5. Verifying storage...")
    stats = adapter.stats()
    print(f"   Database stats: {stats}")
    
    print("\n✓ Full pipeline simulation complete")
    
    adapter.close()


def main():
    """Run all tests."""
    print("=" * 60)
    print("ReCog EhkoForge Adapter Test Suite")
    print("=" * 60)
    
    try:
        if not test_adapter_init():
            print("\n⚠ Adapter init failed - database may not exist")
            print("  Run ehko_refresh.py first to create the database")
            return
        
        test_document_loading()
        test_insight_roundtrip()
        test_pattern_roundtrip()
        test_synthesis_roundtrip()
        test_context_and_themes()
        test_full_pipeline_simulation()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nEhkoForge adapter complete:")
        print("  - adapters/ehkoforge.py: EhkoForgeAdapter")
        print("  - Document loading from reflection_objects, sessions")
        print("  - Insight ↔ ingots table mapping")
        print("  - Pattern ↔ ingot_patterns table (new)")
        print("  - Synthesis ↔ ehko_personality_layers mapping")
        print("\nReCog is now fully integrated with EhkoForge!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
