"""
ReCog Core - Phase 2 Test Script (Extractor)

Verifies that the Extractor (Tier 1) works correctly with mock LLM.

Usage:
    cd "5.0 Scripts"
    python test_recog_extractor.py
"""

import sys
import json
from pathlib import Path

# Ensure recog_engine is importable
sys.path.insert(0, str(Path(__file__).parent))

from recog_engine import (
    # Types
    Document,
    Insight,
    # Config
    RecogConfig,
    # LLM
    MockLLMProvider,
    # Signal
    SignalProcessor,
    # Extractor
    Extractor,
    extract_from_text,
    # Adapters
    MemoryAdapter,
)


# Sample LLM response for testing
MOCK_EXTRACTION_RESPONSE = json.dumps({
    "insights": [
        {
            "summary": "User experiences anticipatory anxiety specifically around public speaking and presentation scenarios.",
            "themes": ["anxiety", "public-speaking", "performance-fear"],
            "significance": 0.75,
            "confidence": 0.85,
            "excerpt": "I've been feeling really anxious about the presentation tomorrow."
        },
        {
            "summary": "Self-doubt manifests as catastrophic thinking about potential failure.",
            "themes": ["self-doubt", "catastrophizing", "fear-of-failure"],
            "significance": 0.65,
            "confidence": 0.80,
            "excerpt": "What if I mess up?"
        }
    ],
    "meta": {
        "content_quality": "medium",
        "notes": "Brief content but emotionally significant."
    }
})


def test_mock_llm():
    """Test MockLLMProvider."""
    print("\n=== Testing MockLLMProvider ===")
    
    mock = MockLLMProvider()
    mock.set_default_response(MOCK_EXTRACTION_RESPONSE)
    
    response = mock.generate("Test prompt")
    assert response.success
    assert "insights" in response.content
    print(f"✓ Mock provider returns configured response")
    
    # Test call tracking
    calls = mock.get_calls()
    assert len(calls) == 1
    assert calls[0]["prompt"] == "Test prompt"
    print(f"✓ Call tracking works ({len(calls)} call recorded)")
    
    return mock


def test_extractor_basic(mock_llm):
    """Test basic extraction."""
    print("\n=== Testing Extractor (Basic) ===")
    
    # Create document
    doc = Document.create(
        content="I've been feeling really anxious about the presentation tomorrow. What if I mess up? Everyone will see me fail.",
        source_type="chat",
        source_ref="session_123"
    )
    
    # Process signals
    processor = SignalProcessor()
    processor.process(doc)
    print(f"Signals extracted: {list(doc.signals['flags'].keys())}")
    
    # Extract insights
    config = RecogConfig.for_testing()
    extractor = Extractor(mock_llm, config)
    
    insights = extractor.extract(doc)
    
    print(f"Extracted {len(insights)} insights:")
    for i, insight in enumerate(insights):
        print(f"  {i+1}. {insight.summary[:60]}...")
        print(f"     Themes: {insight.themes}")
        print(f"     Significance: {insight.significance:.2f}")
    
    assert len(insights) == 2
    assert insights[0].themes == ["anxiety", "public-speaking", "performance-fear"]
    print("✓ Basic extraction works")
    
    return insights


def test_extractor_with_adapter(mock_llm):
    """Test extraction with MemoryAdapter."""
    print("\n=== Testing Extractor with Adapter ===")
    
    # Setup adapter with context
    adapter = MemoryAdapter()
    adapter.set_context("This is a personal reflection journal focused on emotional processing.")
    adapter.set_themes(["anxiety", "growth", "self-reflection"])
    
    # Add multiple documents
    docs = [
        Document.create(
            content="I've been feeling really anxious about the presentation tomorrow. What if I mess up?",
            source_type="chat",
            source_ref="session_1"
        ),
        Document.create(
            content="Today I practiced my presentation three times. Each time felt a bit better. Maybe I can do this.",
            source_type="chat",
            source_ref="session_2"
        ),
    ]
    
    for doc in docs:
        adapter.add_document(doc)
        SignalProcessor().process(doc)
    
    # Configure mock for second document
    mock_llm.set_response("practiced", json.dumps({
        "insights": [
            {
                "summary": "Deliberate practice reduces anxiety through incremental confidence building.",
                "themes": ["practice", "confidence", "anxiety-management"],
                "significance": 0.70,
                "confidence": 0.75,
                "excerpt": "Each time felt a bit better."
            }
        ],
        "meta": {"content_quality": "medium"}
    }))
    
    # Extract batch
    config = RecogConfig.for_testing()
    extractor = Extractor(mock_llm, config)
    
    insights, stats = extractor.extract_batch(docs, adapter)
    
    print(f"Stats: {stats}")
    print(f"Total insights: {len(insights)}")
    
    # Check adapter received insights
    saved_insights = adapter.get_insights()
    print(f"Insights saved to adapter: {len(saved_insights)}")
    
    # Check themes aggregated
    all_themes = adapter.get_existing_themes()
    print(f"Themes in adapter: {all_themes}")
    
    assert stats["documents_processed"] == 2
    assert len(saved_insights) >= 2
    print("✓ Batch extraction with adapter works")


def test_insight_deduplication(mock_llm):
    """Test insight similarity and merging."""
    print("\n=== Testing Deduplication ===")
    
    config = RecogConfig(similarity_threshold=0.6)
    extractor = Extractor(mock_llm, config)
    
    # Create two similar insights manually
    insight1 = Insight.create(
        summary="User experiences anxiety about public speaking",
        themes=["anxiety", "public-speaking"],
        significance=0.6,
        confidence=0.8,
        source_ids=["doc1"],
    )
    
    insight2 = Insight.create(
        summary="Anxiety manifests around speaking in public",
        themes=["anxiety", "public-speaking", "fear"],
        significance=0.7,
        confidence=0.75,
        source_ids=["doc2"],
    )
    
    # Check similarity
    is_similar = extractor._is_similar(insight1, insight2)
    print(f"Insights are similar: {is_similar}")
    
    if is_similar:
        # Merge
        original_sources = len(insight1.source_ids)
        insight1.merge_with(insight2)
        print(f"After merge:")
        print(f"  Sources: {insight1.source_ids}")
        print(f"  Themes: {insight1.themes}")
        print(f"  Significance: {insight1.significance:.2f}")
        assert len(insight1.source_ids) == 2
        print("✓ Deduplication and merging works")
    else:
        print("  (Insights not similar enough to merge)")


def test_filtering():
    """Test insight filtering by thresholds."""
    print("\n=== Testing Filtering ===")
    
    # Create mock that returns low-quality insights
    mock = MockLLMProvider()
    mock.set_default_response(json.dumps({
        "insights": [
            {
                "summary": "High quality insight",
                "themes": ["test"],
                "significance": 0.8,
                "confidence": 0.9,
                "excerpt": "Important text"
            },
            {
                "summary": "Low confidence insight",
                "themes": ["test"],
                "significance": 0.7,
                "confidence": 0.2,  # Below threshold
                "excerpt": "Text"
            },
            {
                "summary": "Low significance insight",
                "themes": ["test"],
                "significance": 0.1,  # Below threshold
                "confidence": 0.8,
                "excerpt": "Text"
            }
        ],
        "meta": {"content_quality": "medium"}
    }))
    
    config = RecogConfig(min_confidence=0.5, min_significance=0.3)
    extractor = Extractor(mock, config)
    
    doc = Document.create(
        content="This is test content with enough words to pass the minimum threshold for processing.",
        source_type="test",
        source_ref="test.txt"
    )
    SignalProcessor().process(doc)
    
    insights = extractor.extract(doc)
    
    print(f"Insights after filtering: {len(insights)}")
    for insight in insights:
        print(f"  - {insight.summary[:40]}... (sig={insight.significance:.2f}, conf={insight.confidence:.2f})")
    
    assert len(insights) == 1  # Only high quality should pass
    assert insights[0].summary == "High quality insight"
    print("✓ Filtering by thresholds works")


def test_convenience_function(mock_llm):
    """Test extract_from_text convenience function."""
    print("\n=== Testing extract_from_text ===")
    
    insights = extract_from_text(
        text="I've been feeling really anxious about the presentation tomorrow. What if I mess up?",
        llm=mock_llm,
        source_type="note",
        source_ref="quick_note.txt",
        config=RecogConfig.for_testing(),
    )
    
    print(f"Extracted {len(insights)} insights via convenience function")
    assert len(insights) >= 1
    print("✓ Convenience function works")


def main():
    """Run all tests."""
    print("=" * 60)
    print("ReCog Core Phase 2 Test Suite (Extractor)")
    print("=" * 60)
    
    try:
        mock_llm = test_mock_llm()
        mock_llm.set_default_response(MOCK_EXTRACTION_RESPONSE)
        
        test_extractor_basic(mock_llm)
        test_extractor_with_adapter(mock_llm)
        test_insight_deduplication(mock_llm)
        test_filtering()
        test_convenience_function(mock_llm)
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nPhase 2 implementation complete:")
        print("  - core/config.py: RecogConfig")
        print("  - core/llm.py: LLMProvider, MockLLMProvider")
        print("  - core/extractor.py: Extractor (Tier 1)")
        print("\nNext: Phase 3 - Correlator (Tier 2)")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
