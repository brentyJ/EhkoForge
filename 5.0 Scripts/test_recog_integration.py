"""
ReCog Integration Test - Full Pipeline with Real LLM

Tests the complete ReCog pipeline with actual LLM calls:
1. Load real documents from EhkoForge
2. Extract insights (Tier 1)
3. Correlate patterns (Tier 2)
4. Synthesise conclusions (Tier 3)
5. Save to database via EhkoForge adapter

Usage:
    cd "5.0 Scripts"
    python test_recog_integration.py
    
Prerequisites:
    - .env file with OPENAI_API_KEY or ANTHROPIC_API_KEY
    - ehko_index.db exists (run ehko_refresh.py first)
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from recog_engine import (
    # Types
    Document,
    Insight,
    Pattern,
    Synthesis,
    RecogConfig,
    # Processors
    Extractor,
    Correlator,
    Synthesizer,
    # Adapter
    EhkoForgeAdapter,
)

# LLM wrapper
from recog_engine.core.ehko_llm import create_recog_provider


def test_llm_connection():
    """Test that LLM provider is available."""
    print("\n=== Testing LLM Connection ===")
    
    provider = create_recog_provider()
    
    if provider is None:
        print("✗ No LLM provider configured")
        print("  Check .env file for OPENAI_API_KEY or ANTHROPIC_API_KEY")
        return None
    
    print(f"✓ Provider: {provider.name}")
    print(f"  Model: {provider.model}")
    
    # Quick test
    response = provider.generate("Say 'hello' in one word.", max_tokens=10)
    
    if response.success:
        print(f"✓ Connection test passed: '{response.content.strip()}'")
        return provider
    else:
        print(f"✗ Connection test failed: {response.error}")
        return None


def load_test_documents(adapter, limit=3):
    """Load real documents from EhkoForge."""
    print(f"\n=== Loading Documents (limit {limit}) ===")
    
    documents = []
    for doc in adapter.load_documents(source_type="reflection", vault="Mirrorwell", limit=limit):
        documents.append(doc)
        # Truncate content display
        preview = doc.content[:200].replace('\n', ' ')
        print(f"  [{doc.id}] {doc.metadata.get('title', 'Untitled')}")
        print(f"      {len(doc.content)} chars: {preview}...")
    
    if not documents:
        # Try loading any reflection
        for doc in adapter.load_documents(limit=limit):
            documents.append(doc)
            preview = doc.content[:100].replace('\n', ' ')
            print(f"  [{doc.id}] {doc.metadata.get('title', doc.source_ref)}")
    
    print(f"\n✓ Loaded {len(documents)} document(s)")
    return documents


def test_extraction(provider, documents, config):
    """Test Tier 1: Insight extraction."""
    print("\n=== Testing Extraction (Tier 1) ===")
    
    extractor = Extractor(llm=provider, config=config)
    
    all_insights = []
    
    for doc in documents:
        print(f"\nExtracting from: {doc.metadata.get('title', doc.id)}")
        
        insights = extractor.extract(doc)
        
        print(f"  Found {len(insights)} insight(s)")
        
        for insight in insights:
            print(f"    • [{insight.significance:.2f}] {insight.summary[:80]}...")
            print(f"      Themes: {', '.join(insight.themes[:5])}")
            all_insights.append(insight)
    
    print(f"\n✓ Total insights extracted: {len(all_insights)}")
    return all_insights


def test_correlation(provider, insights, config):
    """Test Tier 2: Pattern correlation."""
    print("\n=== Testing Correlation (Tier 2) ===")
    
    if len(insights) < 2:
        print("  Skipping - need at least 2 insights for correlation")
        return []
    
    # Debug: show theme overlap
    from collections import Counter
    all_themes = []
    for i in insights:
        all_themes.extend(t.lower() for t in i.themes)
    theme_counts = Counter(all_themes)
    print(f"  Theme frequency (top 10):")
    for theme, count in theme_counts.most_common(10):
        print(f"    {theme}: {count}")
    
    correlator = Correlator(llm=provider, config=config)
    
    result = correlator.correlate(insights)
    
    # Handle both tuple (patterns, stats) and list return
    if isinstance(result, tuple):
        patterns, stats = result
        print(f"  Correlation stats: {stats}")
    else:
        patterns = result
    
    print(f"  Found {len(patterns)} pattern(s)")
    
    for pattern in patterns:
        print(f"    • [{pattern.pattern_type.value}] {pattern.summary[:80]}...")
        print(f"      Strength: {pattern.strength:.2f}, Insights: {len(pattern.insight_ids)}")
    
    print(f"\n✓ Total patterns found: {len(patterns)}")
    return patterns


def test_synthesis(provider, patterns, insights, config):
    """Test Tier 3: Deep synthesis."""
    print("\n=== Testing Synthesis (Tier 3) ===")
    
    if not patterns:
        print("  Skipping - need patterns for synthesis")
        return []
    
    synthesizer = Synthesizer(llm=provider, config=config)
    
    result = synthesizer.synthesise(patterns, insights)
    
    # Handle both tuple (syntheses, stats) and list return
    if isinstance(result, tuple):
        syntheses, stats = result
        print(f"  Stats: {stats}")
    else:
        syntheses = result
    
    print(f"  Generated {len(syntheses)} synthesis(es)")
    
    for synth in syntheses:
        print(f"    • [{synth.synthesis_type.value}] {synth.summary[:80]}...")
        print(f"      Significance: {synth.significance:.2f}, Confidence: {synth.confidence:.2f}")
    
    print(f"\n✓ Total syntheses: {len(syntheses)}")
    return syntheses


def test_database_save(adapter, insights, patterns, syntheses):
    """Test saving results to database."""
    print("\n=== Testing Database Save ===")
    
    saved_insights = 0
    saved_patterns = 0
    saved_syntheses = 0
    
    # Save insights
    for insight in insights:
        adapter.save_insight(insight)
        saved_insights += 1
    print(f"  ✓ Saved {saved_insights} insight(s) to ingots table")
    
    # Save patterns
    for pattern in patterns:
        adapter.save_pattern(pattern)
        saved_patterns += 1
    print(f"  ✓ Saved {saved_patterns} pattern(s) to ingot_patterns table")
    
    # Save syntheses
    for synth in syntheses:
        adapter.save_synthesis(synth)
        saved_syntheses += 1
    print(f"  ✓ Saved {saved_syntheses} synthesis(es) to ehko_personality_layers table")
    
    # Verify
    stats = adapter.stats()
    print(f"\n  Database stats after save:")
    print(f"    Reflections: {stats['reflections']}")
    print(f"    Insights: {stats['insights']}")
    print(f"    Patterns: {stats['patterns']}")
    print(f"    Syntheses: {stats['syntheses']}")


def run_full_pipeline():
    """Run the complete integration test."""
    print("=" * 60)
    print("ReCog Integration Test - Full Pipeline")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Check LLM
    provider = test_llm_connection()
    if not provider:
        print("\n❌ Cannot proceed without LLM provider")
        return False
    
    # Step 2: Setup - use testing config with lower thresholds
    config = RecogConfig.for_testing()  # Lower thresholds for testing
    config.correlation_min_cluster = 2  # Allow smaller clusters
    config.synthesis_min_patterns = 1   # Allow synthesis with 1 pattern
    adapter = EhkoForgeAdapter()
    
    print(f"\nConfig: extraction_model={config.extraction_model}")
    print(f"        correlation_model={config.correlation_model}")
    print(f"        synthesis_model={config.synthesis_model}")
    
    # Step 3: Load documents
    documents = load_test_documents(adapter, limit=2)
    if not documents:
        print("\n⚠ No documents found - using sample text")
        documents = [
            Document.create(
                content="""I've been reflecting on my tendency to overthink decisions. 
                It feels like every choice becomes weighted with impossible expectations.
                Maybe this comes from childhood, always trying to get things perfect.
                I notice this pattern especially at work when facing ambiguous situations.""",
                source_type="test",
                source_ref="integration_test",
                metadata={"title": "Integration Test Sample"},
            )
        ]
    
    # Step 4: Extract insights
    insights = test_extraction(provider, documents, config)
    
    # Step 5: Correlate patterns
    patterns = test_correlation(provider, insights, config)
    
    # Step 6: Synthesise conclusions
    syntheses = test_synthesis(provider, patterns, insights, config)
    
    # Step 7: Save to database
    test_database_save(adapter, insights, patterns, syntheses)
    
    adapter.close()
    
    print("\n" + "=" * 60)
    print("✅ INTEGRATION TEST COMPLETE")
    print("=" * 60)
    print(f"\nPipeline summary:")
    print(f"  Documents processed: {len(documents)}")
    print(f"  Insights extracted: {len(insights)}")
    print(f"  Patterns found: {len(patterns)}")
    print(f"  Syntheses generated: {len(syntheses)}")
    
    return True


def main():
    """Entry point."""
    try:
        success = run_full_pipeline()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ INTEGRATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
