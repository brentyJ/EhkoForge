"""
ReCog Core - Phase 4 Test Script (Synthesizer)

Verifies that the Synthesizer (Tier 3) works correctly with mock LLM.

Usage:
    cd "5.0 Scripts"
    python test_recog_synthesizer.py
"""

import sys
import json
from pathlib import Path

# Ensure recog_engine is importable
sys.path.insert(0, str(Path(__file__).parent))

from recog_engine import (
    # Types
    Insight,
    Pattern,
    PatternType,
    Synthesis,
    SynthesisType,
    # Config
    RecogConfig,
    # LLM
    MockLLMProvider,
    # Synthesizer
    Synthesizer,
    synthesise_patterns,
    # Adapters
    MemoryAdapter,
)


def create_test_patterns() -> tuple:
    """Create test patterns and their supporting insights."""
    insights = [
        Insight.create(
            summary="User experiences anticipatory anxiety around public speaking.",
            themes=["anxiety", "public-speaking"],
            significance=0.75,
            confidence=0.85,
            source_ids=["doc1"],
        ),
        Insight.create(
            summary="Anxiety manifests before important presentations.",
            themes=["anxiety", "presentations"],
            significance=0.70,
            confidence=0.80,
            source_ids=["doc2"],
        ),
        Insight.create(
            summary="Preparation helps reduce anxiety symptoms.",
            themes=["coping", "preparation"],
            significance=0.80,
            confidence=0.85,
            source_ids=["doc3"],
        ),
        Insight.create(
            summary="User values being well-prepared over spontaneity.",
            themes=["values", "preparation", "control"],
            significance=0.65,
            confidence=0.75,
            source_ids=["doc4"],
        ),
    ]
    
    patterns = [
        Pattern.create(
            summary="Recurring pattern of anticipatory anxiety around performance situations.",
            pattern_type=PatternType.RECURRING,
            insight_ids=[insights[0].id, insights[1].id],
            strength=0.80,
        ),
        Pattern.create(
            summary="Preparation serves as primary coping mechanism for anxiety.",
            pattern_type=PatternType.CLUSTER,
            insight_ids=[insights[2].id, insights[3].id],
            strength=0.75,
        ),
        Pattern.create(
            summary="Control through preparation is a consistent theme.",
            pattern_type=PatternType.RECURRING,
            insight_ids=[insights[2].id, insights[3].id],
            strength=0.70,
        ),
    ]
    
    return patterns, insights


def test_synthesizer_basic():
    """Test basic synthesis."""
    print("\n=== Testing Synthesizer (Basic) ===")
    
    patterns, insights = create_test_patterns()
    
    mock = MockLLMProvider()
    mock.set_default_response(json.dumps({
        "syntheses": [
            {
                "summary": "Core belief that thorough preparation prevents failure and reduces anxiety. This manifests as a strong drive to control outcomes through advance planning, sometimes at the expense of flexibility.",
                "synthesis_type": "belief",
                "pattern_ids": [patterns[0].id[:8], patterns[1].id[:8]],
                "significance": 0.85,
                "confidence": 0.80
            },
            {
                "summary": "Tendency toward performance anxiety in situations requiring public visibility. This anxiety is managed rather than resolved, with preparation serving as the primary coping mechanism.",
                "synthesis_type": "tendency",
                "pattern_ids": [patterns[0].id[:8], patterns[2].id[:8]],
                "significance": 0.75,
                "confidence": 0.75
            }
        ],
        "meta": {
            "corpus_coherence": "high",
            "notes": "Strong patterns around anxiety and preparation coping."
        }
    }))
    
    config = RecogConfig(synthesis_min_patterns=2, synthesis_significance_threshold=0.5)
    synthesizer = Synthesizer(mock, config)
    
    syntheses, stats = synthesizer.synthesise(patterns, insights)
    
    print(f"Stats: {stats}")
    print(f"Syntheses created: {len(syntheses)}")
    
    for synthesis in syntheses:
        print(f"\n  [{synthesis.synthesis_type.value.upper()}]")
        print(f"  {synthesis.summary[:80]}...")
        print(f"  Significance: {synthesis.significance:.2f}, Confidence: {synthesis.confidence:.2f}")
        print(f"  Supporting patterns: {len(synthesis.pattern_ids)}")
    
    assert len(syntheses) >= 1
    assert syntheses[0].synthesis_type == SynthesisType.BELIEF
    print("\n✓ Basic synthesis works")
    
    return syntheses


def test_synthesizer_with_adapter():
    """Test synthesis with adapter."""
    print("\n=== Testing Synthesizer with Adapter ===")
    
    patterns, insights = create_test_patterns()
    
    adapter = MemoryAdapter()
    adapter.set_context("Personal reflection journal for professional development.")
    
    for insight in insights:
        adapter.save_insight(insight)
    for pattern in patterns:
        adapter.save_pattern(pattern)
    
    mock = MockLLMProvider()
    mock.set_default_response(json.dumps({
        "syntheses": [
            {
                "summary": "Core trait of conscientiousness manifesting as preparation-focused anxiety management.",
                "synthesis_type": "trait",
                "pattern_ids": [patterns[0].id[:8], patterns[1].id[:8]],
                "significance": 0.70,
                "confidence": 0.75
            }
        ],
        "meta": {"corpus_coherence": "medium"}
    }))
    
    config = RecogConfig(synthesis_min_patterns=2, synthesis_significance_threshold=0.5)
    synthesizer = Synthesizer(mock, config)
    
    syntheses, stats = synthesizer.synthesise(patterns, insights, adapter)
    
    print(f"Stats: {stats}")
    
    saved_syntheses = adapter.get_syntheses()
    print(f"Syntheses saved to adapter: {len(saved_syntheses)}")
    
    assert len(saved_syntheses) >= 1
    print("✓ Synthesis with adapter works")


def test_synthesis_types():
    """Test all synthesis types."""
    print("\n=== Testing Synthesis Types ===")
    
    patterns, insights = create_test_patterns()
    
    mock = MockLLMProvider()
    mock.set_default_response(json.dumps({
        "syntheses": [
            {
                "summary": "Perfectionist trait drives excessive preparation.",
                "synthesis_type": "trait",
                "pattern_ids": [patterns[0].id[:8], patterns[1].id[:8]],
                "significance": 0.75,
                "confidence": 0.80
            },
            {
                "summary": "Belief that failure is catastrophic and must be avoided.",
                "synthesis_type": "belief",
                "pattern_ids": [patterns[0].id[:8], patterns[2].id[:8]],
                "significance": 0.70,
                "confidence": 0.75
            },
            {
                "summary": "Tendency to over-prepare at the expense of spontaneity.",
                "synthesis_type": "tendency",
                "pattern_ids": [patterns[1].id[:8], patterns[2].id[:8]],
                "significance": 0.65,
                "confidence": 0.70
            },
            {
                "summary": "Ongoing theme of control vs uncertainty.",
                "synthesis_type": "theme",
                "pattern_ids": [patterns[0].id[:8], patterns[1].id[:8]],
                "significance": 0.80,
                "confidence": 0.85
            }
        ],
        "meta": {"corpus_coherence": "high"}
    }))
    
    config = RecogConfig(synthesis_min_patterns=2, synthesis_significance_threshold=0.5)
    synthesizer = Synthesizer(mock, config)
    
    syntheses, stats = synthesizer.synthesise(patterns, insights)
    
    print(f"Created {len(syntheses)} syntheses:")
    types_found = set()
    for synthesis in syntheses:
        types_found.add(synthesis.synthesis_type)
        print(f"  - {synthesis.synthesis_type.value}: {synthesis.summary[:50]}...")
    
    # Should have multiple types
    assert len(types_found) >= 2
    print(f"\n✓ Found {len(types_found)} synthesis types: {[t.value for t in types_found]}")


def test_synthesis_merging():
    """Test synthesis merging when related."""
    print("\n=== Testing Synthesis Merging ===")
    
    mock = MockLLMProvider()
    config = RecogConfig()
    synthesizer = Synthesizer(mock, config)
    
    synthesis1 = Synthesis.create(
        summary="Short summary about anxiety.",
        synthesis_type=SynthesisType.TRAIT,
        pattern_ids=["p1", "p2"],
        significance=0.7,
        confidence=0.75,
    )
    
    synthesis2 = Synthesis.create(
        summary="Extended summary about anxiety and its manifestation in professional contexts.",
        synthesis_type=SynthesisType.TRAIT,
        pattern_ids=["p2", "p3"],
        significance=0.65,
        confidence=0.70,
    )
    
    # Check if related
    related = synthesizer._syntheses_related(synthesis1, synthesis2)
    print(f"Syntheses are related: {related}")
    assert related, "Syntheses with shared patterns and same type should be related"
    
    # Test merge
    original_sig = synthesis1.significance
    synthesizer._merge_syntheses(synthesis1, synthesis2)
    
    print(f"After merge:")
    print(f"  Pattern IDs: {synthesis1.pattern_ids}")
    print(f"  Significance: {synthesis1.significance:.2f} (was {original_sig:.2f})")
    print(f"  Summary: {synthesis1.summary[:60]}...")
    
    assert len(synthesis1.pattern_ids) == 3
    assert synthesis1.significance >= original_sig
    assert "Extended" in synthesis1.summary  # Should keep longer summary
    print("✓ Synthesis merging works")


def test_significance_filtering():
    """Test that low-significance syntheses are filtered."""
    print("\n=== Testing Significance Filtering ===")
    
    patterns, insights = create_test_patterns()
    
    mock = MockLLMProvider()
    mock.set_default_response(json.dumps({
        "syntheses": [
            {
                "summary": "High significance synthesis.",
                "synthesis_type": "belief",
                "pattern_ids": [patterns[0].id[:8], patterns[1].id[:8]],
                "significance": 0.80,
                "confidence": 0.85
            },
            {
                "summary": "Low significance synthesis that should be filtered.",
                "synthesis_type": "trait",
                "pattern_ids": [patterns[0].id[:8], patterns[2].id[:8]],
                "significance": 0.30,  # Below threshold
                "confidence": 0.70
            }
        ],
        "meta": {"corpus_coherence": "medium"}
    }))
    
    config = RecogConfig(
        synthesis_min_patterns=2,
        synthesis_significance_threshold=0.5  # Filter below 0.5
    )
    synthesizer = Synthesizer(mock, config)
    
    syntheses, stats = synthesizer.synthesise(patterns, insights)
    
    print(f"Syntheses after filtering: {len(syntheses)}")
    for s in syntheses:
        print(f"  - {s.summary[:40]}... (sig={s.significance:.2f})")
    
    assert len(syntheses) == 1
    assert syntheses[0].significance >= 0.5
    print("✓ Significance filtering works")


def test_convenience_function():
    """Test synthesise_patterns convenience function."""
    print("\n=== Testing synthesise_patterns ===")
    
    patterns, insights = create_test_patterns()
    
    mock = MockLLMProvider()
    mock.set_default_response(json.dumps({
        "syntheses": [
            {
                "summary": "Test synthesis via convenience function.",
                "synthesis_type": "theme",
                "pattern_ids": [patterns[0].id[:8], patterns[1].id[:8]],
                "significance": 0.70,
                "confidence": 0.75
            }
        ],
        "meta": {"corpus_coherence": "medium"}
    }))
    
    config = RecogConfig(synthesis_min_patterns=2, synthesis_significance_threshold=0.5)
    syntheses = synthesise_patterns(patterns, mock, insights, config)
    
    print(f"Created {len(syntheses)} synthesis via convenience function")
    assert len(syntheses) >= 1
    print("✓ Convenience function works")


def main():
    """Run all tests."""
    print("=" * 60)
    print("ReCog Core Phase 4 Test Suite (Synthesizer)")
    print("=" * 60)
    
    try:
        test_synthesizer_basic()
        test_synthesizer_with_adapter()
        test_synthesis_types()
        test_synthesis_merging()
        test_significance_filtering()
        test_convenience_function()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nPhase 4 implementation complete:")
        print("  - core/synthesizer.py: Synthesizer (Tier 3)")
        print("  - Synthesis types: trait, belief, tendency, theme")
        print("  - Synthesis merging for related conclusions")
        print("  - Significance filtering")
        print("\nReCog Core v1.0 pipeline complete!")
        print("  Tier 0: Signal → Tier 1: Extract → Tier 2: Correlate → Tier 3: Synthesise")
        print("\nNext: EhkoForge adapter (maps ReCog types to ingots/personality layers)")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
