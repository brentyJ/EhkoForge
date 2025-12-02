#!/usr/bin/env python3
"""
Test script for OpenAI integration and multi-provider fallback.

Tests:
1. Provider initialization (Claude + OpenAI)
2. Role-based routing
3. Fallback chain when providers unavailable
4. Cost estimation for different operations
5. Single-provider warning logic

Usage:
    python test_openai_integration.py
    
Environment:
    ANTHROPIC_API_KEY - Claude access
    OPENAI_API_KEY - OpenAI access
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ehkoforge.llm import (
    LLMConfig,
    ClaudeProvider,
    OpenAIProvider,
    ProviderFactory,
    get_provider_for_processing,
    get_provider_for_conversation,
)


def load_env_file():
    """Load .env file if it exists."""
    env_path = project_root / ".env"
    if env_path.exists():
        print(f"📄 Loading environment from {env_path}")
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, _, value = line.partition("=")
                    os.environ[key.strip()] = value.strip()


def check_api_keys():
    """Check which API keys are available."""
    anthropic = os.environ.get("ANTHROPIC_API_KEY")
    openai = os.environ.get("OPENAI_API_KEY")
    
    print("\n🔑 API Key Status:")
    print(f"  ANTHROPIC_API_KEY: {'✅ SET' if anthropic else '❌ NOT SET'}")
    print(f"  OPENAI_API_KEY:    {'✅ SET' if openai else '❌ NOT SET'}")
    
    return anthropic, openai


def prompt_for_keys():
    """Prompt user for missing API keys."""
    anthropic = os.environ.get("ANTHROPIC_API_KEY")
    openai = os.environ.get("OPENAI_API_KEY")
    
    if not anthropic:
        print("\n⚠️  Anthropic API key not found.")
        key = input("Enter ANTHROPIC_API_KEY (or press Enter to skip): ").strip()
        if key:
            os.environ["ANTHROPIC_API_KEY"] = key
            anthropic = key
    
    if not openai:
        print("\n⚠️  OpenAI API key not found.")
        key = input("Enter OPENAI_API_KEY (or press Enter to skip): ").strip()
        if key:
            os.environ["OPENAI_API_KEY"] = key
            openai = key
    
    return anthropic, openai


def test_provider_init(anthropic_key, openai_key):
    """Test direct provider initialization."""
    print("\n" + "="*60)
    print("TEST 1: Direct Provider Initialization")
    print("="*60)
    
    results = {}
    
    # Test Claude
    if anthropic_key:
        try:
            claude = ClaudeProvider(api_key=anthropic_key)
            print(f"✅ ClaudeProvider initialized")
            print(f"   Model: {claude.model}")
            results['claude'] = True
        except Exception as e:
            print(f"❌ ClaudeProvider failed: {e}")
            results['claude'] = False
    else:
        print("⏭️  Skipping Claude (no API key)")
        results['claude'] = None
    
    # Test OpenAI
    if openai_key:
        try:
            openai_provider = OpenAIProvider(api_key=openai_key)
            print(f"✅ OpenAIProvider initialized")
            print(f"   Model: {openai_provider.model}")
            results['openai'] = True
        except Exception as e:
            print(f"❌ OpenAIProvider failed: {e}")
            results['openai'] = False
    else:
        print("⏭️  Skipping OpenAI (no API key)")
        results['openai'] = None
    
    return results


def test_config_loading():
    """Test LLMConfig loading from environment."""
    print("\n" + "="*60)
    print("TEST 2: Config Loading")
    print("="*60)
    
    config = LLMConfig.from_env()
    
    print(f"\n📋 Configuration:")
    print(f"   Default provider: {config.default_provider}")
    print(f"   Max tokens: {config.max_tokens}")
    print(f"   Temperature: {config.temperature}")
    
    print(f"\n🎯 Role-Based Routing:")
    print(f"   Processing: {config.processing_provider} / {config.processing_model}")
    print(f"   Conversation: {config.conversation_provider} / {config.conversation_model}")
    print(f"   Ehko: {config.ehko_provider} / {config.ehko_model}")
    
    print(f"\n🔌 Available Providers:")
    for name, provider in config.providers.items():
        status = "✅" if provider.enabled and provider.api_key else "❌"
        print(f"   {status} {name} (priority: {provider.priority})")
    
    # Check fallback chain
    print(f"\n⛓️  Fallback Chain:")
    chain = config.get_fallback_chain()
    for i, provider in enumerate(chain, 1):
        print(f"   {i}. {provider.name} ({provider.model or 'default'})")
    
    return config


def test_role_routing(config):
    """Test role-based provider routing."""
    print("\n" + "="*60)
    print("TEST 3: Role-Based Provider Routing")
    print("="*60)
    
    # Test processing role
    print("\n🔧 Processing Role:")
    try:
        proc_provider = get_provider_for_processing(config)
        print(f"   ✅ Provider: {proc_provider.PROVIDER_NAME}")
        print(f"   ✅ Model: {proc_provider.model}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test conversation role
    print("\n💬 Conversation Role:")
    try:
        conv_provider = get_provider_for_conversation(config)
        print(f"   ✅ Provider: {conv_provider.PROVIDER_NAME}")
        print(f"   ✅ Model: {conv_provider.model}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")


def test_single_provider_warning(config):
    """Test single-provider mode detection and warning."""
    print("\n" + "="*60)
    print("TEST 4: Single-Provider Mode Detection")
    print("="*60)
    
    enabled_providers = [p for p in config.providers.values() if p.enabled and p.api_key]
    
    if len(enabled_providers) == 0:
        print("\n❌ CRITICAL: No API keys configured")
        print("   System cannot function without at least one provider.")
        return
    
    if len(enabled_providers) == 1:
        provider = enabled_providers[0]
        print(f"\n⚠️  SINGLE-PROVIDER MODE DETECTED")
        print(f"\n   Running with {provider.name.upper()} only.")
        print(f"\n   EhkoForge is optimised for dual-LLM usage:")
        print(f"   • Claude Sonnet: Conversation quality, Ehko personality")
        print(f"   • GPT-4o-mini: Cost-effective processing (ingot extraction)")
        print(f"\n   Running with {provider.name} only:")
        
        if provider.name == "openai":
            print(f"   • Ehko personality may be less nuanced")
            print(f"   • Conversation quality depends on model:")
            if "mini" in provider.model:
                print(f"     - gpt-4o-mini: Acceptable for processing, weak for Ehko")
            else:
                print(f"     - gpt-4o: Good quality, higher cost")
        
        if provider.name == "claude":
            print(f"   • Processing costs 5x higher (~$15/MTok vs $3/MTok)")
            print(f"   • Conversation quality excellent")
            print(f"   • Ehko personality excellent")
        
        print(f"\n   To optimise, add second API key in .env file.")
    else:
        print(f"\n✅ DUAL-PROVIDER MODE")
        print(f"   {len(enabled_providers)} providers configured - optimal setup")


def estimate_costs():
    """Show cost estimates for typical operations."""
    print("\n" + "="*60)
    print("TEST 5: Cost Estimation")
    print("="*60)
    
    print("\n💰 Estimated Costs (per 1M tokens):")
    print("\n   Claude Sonnet 4:")
    print("     Input:  $3.00")
    print("     Output: $15.00")
    
    print("\n   GPT-4o:")
    print("     Input:  $2.50")
    print("     Output: $10.00")
    
    print("\n   GPT-4o-mini:")
    print("     Input:  $0.15")
    print("     Output: $0.60")
    
    print("\n📊 Typical Operations:")
    print("\n   Ingot extraction (processing):")
    print("     • 1000 tokens input, 500 output")
    print("     • GPT-4o-mini: ~$0.00045")
    print("     • Claude Sonnet: ~$0.01050 (23x more)")
    
    print("\n   Conversation turn:")
    print("     • 2000 tokens input, 500 output")
    print("     • Claude Sonnet: ~$0.01350")
    print("     • GPT-4o: ~$0.01000 (similar)")
    
    print("\n   Monthly estimate (100 ingots + 50 conversations):")
    print("     • Dual-provider (optimal): ~$0.72")
    print("     • Claude only: ~$1.73 (2.4x)")
    print("     • OpenAI only (gpt-4o): ~$0.95")


def test_api_call(provider, provider_name):
    """Test actual API call."""
    print(f"\n🧪 Testing {provider_name} API call...")
    
    try:
        response = provider.generate(
            prompt="Say 'Hello from EhkoForge' and nothing else.",
            max_tokens=50,
            temperature=0.7,
        )
        
        if response.success:
            print(f"   ✅ Success!")
            print(f"   Response: {response.content[:100]}")
            if hasattr(response, 'usage') and response.usage:
                print(f"   Tokens: {response.usage.get('total_tokens', 'N/A')}")
        else:
            print(f"   ❌ Failed: {response.error}")
            
        return response.success
        
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("EHKOFORGE OPENAI INTEGRATION TEST")
    print("="*60)
    
    # Load environment
    load_env_file()
    
    # Check keys
    anthropic_key, openai_key = check_api_keys()
    
    # Prompt if needed
    if not anthropic_key or not openai_key:
        print("\n⚠️  Missing API keys. Please provide them to continue.")
        anthropic_key, openai_key = prompt_for_keys()
    
    if not anthropic_key and not openai_key:
        print("\n❌ No API keys provided. Cannot test.")
        print("   Set ANTHROPIC_API_KEY and/or OPENAI_API_KEY in environment or .env file.")
        return
    
    # Run tests
    provider_results = test_provider_init(anthropic_key, openai_key)
    config = test_config_loading()
    test_role_routing(config)
    test_single_provider_warning(config)
    estimate_costs()
    
    # Optional: Test actual API calls
    print("\n" + "="*60)
    print("TEST 6: Live API Calls (Optional)")
    print("="*60)
    print("\n⚠️  This will make real API calls and cost ~$0.001")
    
    response = input("\nRun live API tests? (y/N): ").strip().lower()
    
    if response == 'y':
        if provider_results.get('claude') and anthropic_key:
            claude = ClaudeProvider(api_key=anthropic_key)
            test_api_call(claude, "Claude")
        
        if provider_results.get('openai') and openai_key:
            openai_provider = OpenAIProvider(api_key=openai_key)
            test_api_call(openai_provider, "OpenAI")
    else:
        print("   ⏭️  Skipped")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    print("\n✅ Integration tests complete.")
    print("\nNext steps:")
    print("  1. Start forge_server.py")
    print("  2. Check /api/llm/status endpoint")
    print("  3. Test chat with Claude")
    print("  4. Test ingot processing with GPT-4o-mini")


if __name__ == "__main__":
    main()
