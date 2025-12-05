"""
ReCog Core - Phase 1 Test Script

Verifies that the core types, signal processor, and memory adapter work correctly.

Usage:
    cd "5.0 Scripts"
    python test_recog_core.py
"""

import sys
from pathlib import Path

# Ensure recog_engine is importable
sys.path.insert(0, str(Path(__file__).parent))

from recog_engine import (
    # Types
    Document,
    Insight,
    Pattern,
    Synthesis,
    PatternType,
    SynthesisType,
    ProcessingState,
    Corpus,
    # Signal
    SignalProcessor,
    process_text,
    process_document,
    # Adapters
    MemoryAdapter,
)


def test_document_creation():
    """Test Document creation and serialisation."""
    print("\n=== Testing Document ===")
    
    doc = Document.create(
        content="I've been feeling really anxious about the presentation tomorrow. What if I mess up?",
        source_type="chat",
        source_ref="session_123",
        metadata={"session_id": "123"}
    )
    
    print(f"Created: {doc.id[:8]}...")
    print(f"Content length: {len(doc.content)} chars")
    print(f"Source: {doc.source_type}/{doc.source_ref}")
    
    # Test serialisation
    data = doc.to_dict()
    restored = Document.from_dict(data)
    assert restored.id == doc.id
    assert restored.content == doc.content
    print("✓ Serialisation round-trip OK")
    
    return doc


def test_signal_processor(doc: Document):
    """Test Signal processor."""
    print("\n=== Testing Signal Processor ===")
    
    processor = SignalProcessor()
    processed = processor.process(doc)
    
    signals = processed.signals
    print(f"Word count: {signals['word_count']}")
    print(f"Emotion keywords: {signals['emotion_signals']['keywords_found']}")
    print(f"Categories: {signals['emotion_signals']['categories']}")
    print(f"Questions: {signals['question_analysis']['question_count']}")
    print(f"Self-inquiry: {signals['question_analysis']['self_inquiry']}")
    print(f"Flags: {[k for k, v in signals['flags'].items() if v]}")
    
    # Test summarisation
    summary = processor.summarise_for_prompt(signals)
    print(f"\nPrompt summary:\n{summary}")
    
    print("✓ Signal processing OK")
    return processed


def test_insight_creation():
    """Test Insight creation and merging."""
    print("\n=== Testing Insight ===")
    
    insight1 = Insight.create(
        summary="User experiences anticipatory anxiety around public speaking",
        themes=["anxiety", "public-speaking", "self-doubt"],
        significance=0.7,
        confidence=0.8,
        source_ids=["doc_1"],
        excerpts=["feeling really anxious about the presentation"],
    )
    
    print(f"Created insight: {insight1.id[:8]}...")
    print(f"Significance: {insight1.significance}")
    
    # Test merging
    insight2 = Insight.create(
        summary="Presentation anxiety is a recurring theme",
        themes=["anxiety", "work", "performance"],
        significance=0.6,
        confidence=0.7,
        source_ids=["doc_2"],
        excerpts=["worried about messing up"],
    )
    
    insight1.merge_with(insight2)
    print(f"After merge - Significance: {insight1.significance:.2f}")
    print(f"After merge - Sources: {len(insight1.source_ids)}")
    print(f"After merge - Themes: {insight1.themes}")
    print("✓ Insight merge OK")
    
    return insight1


def test_pattern_creation(insight: Insight):
    """Test Pattern creation."""
    print("\n=== Testing Pattern ===")
    
    pattern = Pattern.create(
        summary="Recurring anxiety pattern around performance situations",
        pattern_type=PatternType.RECURRING,
        insight_ids=[insight.id],
        strength=0.75,
        metadata={"frequency": "weekly"}
    )
    
    print(f"Created pattern: {pattern.id[:8]}...")
    print(f"Type: {pattern.pattern_type.value}")
    print(f"Strength: {pattern.strength}")
    
    # Test serialisation
    data = pattern.to_dict()
    restored = Pattern.from_dict(data)
    assert restored.pattern_type == PatternType.RECURRING
    print("✓ Pattern serialisation OK")
    
    return pattern


def test_memory_adapter():
    """Test MemoryAdapter."""
    print("\n=== Testing Memory Adapter ===")
    
    adapter = MemoryAdapter()
    
    # Add documents
    doc1 = Document.create(
        content="First document about anxiety",
        source_type="note",
        source_ref="note1.txt"
    )
    doc2 = Document.create(
        content="Second document about happiness",
        source_type="chat",
        source_ref="session_1"
    )
    
    adapter.add_documents([doc1, doc2])
    print(f"Added 2 documents")
    
    # Test filtering
    notes = list(adapter.load_documents(source_type="note"))
    assert len(notes) == 1
    print(f"✓ Filtered by source_type: found {len(notes)}")
    
    # Add insights
    insight = Insight.create(
        summary="Test insight",
        themes=["test", "demo"],
        significance=0.5,
        confidence=0.9,
        source_ids=[doc1.id],
    )
    adapter.save_insight(insight)
    
    # Test insight retrieval
    all_insights = adapter.get_insights()
    assert len(all_insights) == 1
    print(f"✓ Saved and retrieved {len(all_insights)} insight")
    
    # Test filtering by significance
    high_sig = adapter.get_insights(min_significance=0.7)
    assert len(high_sig) == 0
    print(f"✓ Significance filter working")
    
    # Test context
    adapter.set_context("This is domain context")
    assert adapter.get_context() == "This is domain context"
    print(f"✓ Context management working")
    
    # Test theme aggregation
    adapter.set_themes(["existing-theme"])
    themes = adapter.get_existing_themes()
    assert "test" in themes  # From insight
    assert "existing-theme" in themes  # Manually set
    print(f"✓ Theme aggregation: {len(themes)} themes")
    
    # Stats
    stats = adapter.stats()
    print(f"Stats: {stats}")
    print(f"✓ Memory adapter OK")
    
    return adapter


def test_corpus():
    """Test Corpus container."""
    print("\n=== Testing Corpus ===")
    
    corpus = Corpus.create(
        name="Test Corpus",
        config={"max_passes": 3}
    )
    
    doc = Document.create(
        content="Test content",
        source_type="test",
        source_ref="test.txt"
    )
    corpus.add_document(doc)
    
    insight = Insight.create(
        summary="Test insight",
        themes=["test"],
        significance=0.5,
        confidence=0.9,
        source_ids=[doc.id],
    )
    corpus.add_insight(insight)
    
    print(f"Corpus: {corpus.name}")
    print(f"Documents: {len(corpus.documents)}")
    print(f"Insights: {len(corpus.insights)}")
    
    # Test retrieval
    found_doc = corpus.get_document(doc.id)
    assert found_doc is not None
    print("✓ Corpus container OK")


def main():
    """Run all tests."""
    print("=" * 60)
    print("ReCog Core Phase 1 Test Suite")
    print("=" * 60)
    
    try:
        doc = test_document_creation()
        test_signal_processor(doc)
        insight = test_insight_creation()
        test_pattern_creation(insight)
        test_memory_adapter()
        test_corpus()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nPhase 1 implementation complete:")
        print("  - core/types.py: Document, Insight, Pattern, Synthesis")
        print("  - core/signal.py: SignalProcessor (Tier 0)")
        print("  - adapters/base.py: RecogAdapter interface")
        print("  - adapters/memory.py: MemoryAdapter for testing")
        print("\nNext: Phase 2 - Extractor (Tier 1)")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
