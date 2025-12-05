"""
ReCog Core - Phase 3 Test Script (Correlator)

Verifies that the Correlator (Tier 2) works correctly with mock LLM.

Usage:
    cd "5.0 Scripts"
    python test_recog_correlator.py
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
    # Config
    RecogConfig,
    # LLM
    MockLLMProvider,
    # Correlator
    Correlator,
    find_patterns,
    # Adapters
    MemoryAdapter,
)


def create_test_insights() -> list:
    """Create a set of test insights for correlation."""
    return [
        Insight.create(
            summary="User experiences anticipatory anxiety specifically around public speaking.",
            themes=["anxiety", "public-speaking", "performance"],
            significance=0.75,
            confidence=0.85,
            source_ids=["doc1"],
        ),
        Insight.create(
            summary="Anxiety manifests before important presentations at work.",
            themes=["anxiety", "work", "presentations", "performance"],
            significance=0.70,
            confidence=0.80,
            source_ids=["doc2"],
        ),
        Insight.create(
            summary="Physical symptoms of nervousness appear before speaking events.",
            themes=["anxiety", "physical-symptoms", "public-speaking"],
            significance=0.65,
            confidence=0.75,
            source_ids=["doc3"],
        ),
        Insight.create(
            summary="Practice and preparation help reduce pre-presentation anxiety.",
            themes=["anxiety", "coping", "preparation", "presentations"],
            significance=0.80,
            confidence=0.85,
            source_ids=["doc4"],
        ),
        Insight.create(
            summary="User values deep connections over surface-level socialising.",
            themes=["relationships", "introversion", "values"],
            significance=0.70,
            confidence=0.80,
            source_ids=["doc5"],
        ),
    ]


def test_theme_clustering():
    """Test insight clustering by themes."""
    print("\n=== Testing Theme Clustering ===")
    
    insights = create_test_insights()
    
    mock = MockLLMProvider()
    config = RecogConfig(correlation_min_cluster=2)  # Lower threshold for testing
    correlator = Correlator(mock, config)
    
    clusters = correlator._cluster_by_themes(insights)
    
    print(f"Found {len(clusters)} clusters:")
    for themes, cluster_insights in clusters.items():
        print(f"  - '{themes}': {len(cluster_insights)} insights")
        for insight in cluster_insights:
            print(f"      {insight.summary[:50]}...")
    
    # Should find anxiety cluster
    anxiety_found = any("anxiety" in themes for themes in clusters.keys())
    assert anxiety_found, "Should find anxiety-related cluster"
    print("✓ Theme clustering works")
    
    return clusters


def test_correlator_basic():
    """Test basic correlation."""
    print("\n=== Testing Correlator (Basic) ===")
    
    insights = create_test_insights()
    
    # Create mock with pattern response
    mock = MockLLMProvider()
    
    # Response for anxiety cluster
    mock.set_response("anxiety", json.dumps({
        "patterns": [
            {
                "summary": "Recurring pattern of anticipatory anxiety around public speaking and presentations.",
                "pattern_type": "recurring",
                "insight_ids": [insights[0].id[:8], insights[1].id[:8], insights[2].id[:8]],
                "strength": 0.85
            },
            {
                "summary": "Coping strategy: preparation reduces anxiety symptoms.",
                "pattern_type": "cluster",
                "insight_ids": [insights[2].id[:8], insights[3].id[:8]],
                "strength": 0.70
            }
        ],
        "meta": {
            "cluster_coherence": "high",
            "notes": "Strong recurring theme of presentation anxiety."
        }
    }))
    
    config = RecogConfig(correlation_min_cluster=2)
    correlator = Correlator(mock, config)
    
    patterns, stats = correlator.correlate(insights)
    
    print(f"Stats: {stats}")
    print(f"Patterns found: {len(patterns)}")
    
    for pattern in patterns:
        print(f"  - [{pattern.pattern_type.value}] {pattern.summary[:60]}...")
        print(f"    Strength: {pattern.strength:.2f}, Insights: {len(pattern.insight_ids)}")
    
    assert len(patterns) >= 1
    assert patterns[0].pattern_type == PatternType.RECURRING
    print("✓ Basic correlation works")
    
    return patterns


def test_correlator_with_adapter():
    """Test correlation with adapter."""
    print("\n=== Testing Correlator with Adapter ===")
    
    insights = create_test_insights()
    
    # Setup adapter
    adapter = MemoryAdapter()
    adapter.set_context("Personal reflection journal focused on professional development and self-awareness.")
    
    for insight in insights:
        adapter.save_insight(insight)
    
    # Create mock
    mock = MockLLMProvider()
    mock.set_default_response(json.dumps({
        "patterns": [
            {
                "summary": "Performance anxiety is a recurring theme across multiple reflections.",
                "pattern_type": "recurring",
                "insight_ids": [insights[0].id[:8], insights[1].id[:8]],
                "strength": 0.75
            }
        ],
        "meta": {"cluster_coherence": "medium"}
    }))
    
    config = RecogConfig(correlation_min_cluster=2)
    correlator = Correlator(mock, config)
    
    patterns, stats = correlator.correlate(insights, adapter)
    
    print(f"Stats: {stats}")
    
    # Check patterns saved to adapter
    saved_patterns = adapter.get_patterns()
    print(f"Patterns saved to adapter: {len(saved_patterns)}")
    
    assert len(saved_patterns) >= 1
    print("✓ Correlation with adapter works")


def test_pattern_types():
    """Test different pattern type detection."""
    print("\n=== Testing Pattern Types ===")
    
    # Create insights with contradiction
    insights = [
        Insight.create(
            summary="User believes they are introverted and need alone time.",
            themes=["introversion", "self-perception", "energy"],
            significance=0.7,
            confidence=0.8,
            source_ids=["doc1"],
        ),
        Insight.create(
            summary="User feels energised after social gatherings.",
            themes=["socialising", "energy", "self-perception"],
            significance=0.65,
            confidence=0.75,
            source_ids=["doc2"],
        ),
        Insight.create(
            summary="User identifies as someone who dislikes parties.",
            themes=["introversion", "socialising", "self-perception"],
            significance=0.6,
            confidence=0.7,
            source_ids=["doc3"],
        ),
    ]
    
    mock = MockLLMProvider()
    mock.set_default_response(json.dumps({
        "patterns": [
            {
                "summary": "Contradiction between stated introversion and reported energy from socialising.",
                "pattern_type": "contradiction",
                "insight_ids": [insights[0].id[:8], insights[1].id[:8]],
                "strength": 0.70
            }
        ],
        "meta": {"cluster_coherence": "medium"}
    }))
    
    config = RecogConfig(correlation_min_cluster=2)
    correlator = Correlator(mock, config)
    
    patterns, stats = correlator.correlate(insights)
    
    print(f"Found {len(patterns)} pattern(s)")
    for pattern in patterns:
        print(f"  - Type: {pattern.pattern_type.value}")
        print(f"    {pattern.summary}")
    
    # Should detect contradiction
    has_contradiction = any(p.pattern_type == PatternType.CONTRADICTION for p in patterns)
    assert has_contradiction, "Should detect contradiction pattern"
    print("✓ Pattern type detection works")


def test_pattern_merging():
    """Test pattern merging when overlapping."""
    print("\n=== Testing Pattern Merging ===")
    
    mock = MockLLMProvider()
    config = RecogConfig()
    correlator = Correlator(mock, config)
    
    pattern1 = Pattern.create(
        summary="Pattern about anxiety",
        pattern_type=PatternType.RECURRING,
        insight_ids=["id1", "id2", "id3"],
        strength=0.7,
    )
    
    pattern2 = Pattern.create(
        summary="Extended pattern about anxiety and coping",
        pattern_type=PatternType.RECURRING,
        insight_ids=["id2", "id3", "id4"],
        strength=0.6,
    )
    
    # Check overlap detection
    overlaps = correlator._patterns_overlap(pattern1, pattern2)
    print(f"Patterns overlap: {overlaps}")
    assert overlaps, "Patterns with 50%+ shared insights should overlap"
    
    # Test merge
    original_strength = pattern1.strength
    correlator._merge_patterns(pattern1, pattern2)
    
    print(f"After merge:")
    print(f"  Insight IDs: {pattern1.insight_ids}")
    print(f"  Strength: {pattern1.strength:.2f} (was {original_strength:.2f})")
    print(f"  Summary: {pattern1.summary}")
    
    assert len(pattern1.insight_ids) == 4
    assert pattern1.strength > original_strength
    print("✓ Pattern merging works")


def test_convenience_function():
    """Test find_patterns convenience function."""
    print("\n=== Testing find_patterns ===")
    
    insights = create_test_insights()[:3]
    
    mock = MockLLMProvider()
    mock.set_default_response(json.dumps({
        "patterns": [
            {
                "summary": "Test pattern",
                "pattern_type": "cluster",
                "insight_ids": [insights[0].id[:8], insights[1].id[:8]],
                "strength": 0.6
            }
        ],
        "meta": {"cluster_coherence": "medium"}
    }))
    
    config = RecogConfig(correlation_min_cluster=2)
    patterns = find_patterns(insights, mock, config)
    
    print(f"Found {len(patterns)} pattern(s) via convenience function")
    assert len(patterns) >= 1
    print("✓ Convenience function works")


def main():
    """Run all tests."""
    print("=" * 60)
    print("ReCog Core Phase 3 Test Suite (Correlator)")
    print("=" * 60)
    
    try:
        test_theme_clustering()
        test_correlator_basic()
        test_correlator_with_adapter()
        test_pattern_types()
        test_pattern_merging()
        test_convenience_function()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nPhase 3 implementation complete:")
        print("  - core/correlator.py: Correlator (Tier 2)")
        print("  - Theme-based clustering")
        print("  - Pattern detection (recurring, contradiction, evolution, cluster)")
        print("  - Pattern merging for overlapping insights")
        print("\nNext: Phase 4 - Synthesizer (Tier 3) + EhkoForge adapter")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
