#!/usr/bin/env python3
"""
Test Mana Management System

Tests all new mana-related endpoints and functionality.
Run with server running: python test_mana_system.py
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_mana_balance():
    """Test GET /api/mana/balance"""
    print("\n" + "=" * 60)
    print("TEST: Mana Balance")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/mana/balance")
    data = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"Success: {data.get('success')}")
    print(f"Balance: {json.dumps(data.get('balance'), indent=2)}")
    print(f"Limits: {json.dumps(data.get('limits'), indent=2)}")
    
    return response.status_code == 200


def test_mana_config():
    """Test GET /api/mana/config"""
    print("\n" + "=" * 60)
    print("TEST: Mana Configuration")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/mana/config")
    data = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"Success: {data.get('success')}")
    print(f"Config: {json.dumps(data.get('config'), indent=2)}")
    
    return response.status_code == 200


def test_set_config():
    """Test POST /api/mana/config"""
    print("\n" + "=" * 60)
    print("TEST: Update Configuration (switch to BYOK mode)")
    print("=" * 60)
    
    payload = {
        "mana_mode": "byok",
        "byok_max_mana": 150.0,
        "byok_regen_rate": 2.0,
    }
    
    response = requests.post(f"{BASE_URL}/api/mana/config", json=payload)
    data = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"Success: {data.get('success')}")
    print(f"Updated Config: {json.dumps(data.get('config'), indent=2)}")
    
    # Reset to mana mode
    requests.post(f"{BASE_URL}/api/mana/config", json={"mana_mode": "mana"})
    
    return response.status_code == 200


def test_pricing():
    """Test GET /api/mana/pricing"""
    print("\n" + "=" * 60)
    print("TEST: Pricing Tiers")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/mana/pricing")
    data = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"Success: {data.get('success')}")
    print(f"Tiers: {json.dumps(data.get('tiers'), indent=2)}")
    
    return response.status_code == 200


def test_purchase():
    """Test POST /api/mana/purchase (simulated)"""
    print("\n" + "=" * 60)
    print("TEST: Mana Purchase (simulated)")
    print("=" * 60)
    
    payload = {"tier_id": 2}  # Ember tier (25,000 mana for $20)
    
    response = requests.post(f"{BASE_URL}/api/mana/purchase", json=payload)
    data = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"Success: {data.get('success')}")
    print(f"Purchase ID: {data.get('purchase_id')}")
    print(f"New Balance: {json.dumps(data.get('balance'), indent=2)}")
    
    return response.status_code == 200


def test_history():
    """Test GET /api/mana/history"""
    print("\n" + "=" * 60)
    print("TEST: Purchase & Usage History")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/mana/history?limit=5&days=30")
    data = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"Success: {data.get('success')}")
    print(f"Purchases ({len(data.get('purchases', []))}):")
    for purchase in data.get('purchases', [])[:3]:
        print(f"  - {purchase.get('amount_mana')} mana for ${purchase.get('cost_usd')}")
    print(f"Usage Stats: {json.dumps(data.get('usage', {}).get('totals'), indent=2)}")
    
    return response.status_code == 200


def test_api_keys():
    """Test GET /api/mana/api-keys"""
    print("\n" + "=" * 60)
    print("TEST: API Keys (BYOK)")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/mana/api-keys")
    data = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"Success: {data.get('success')}")
    print(f"Keys: {json.dumps(data.get('keys'), indent=2)}")
    
    return response.status_code == 200


def main():
    print("=" * 60)
    print("MANA MANAGEMENT SYSTEM TEST SUITE")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print("\nMake sure forge_server.py is running!")
    input("Press Enter to continue...")
    
    tests = [
        ("Mana Balance", test_mana_balance),
        ("Mana Config (GET)", test_mana_config),
        ("Set Config (POST)", test_set_config),
        ("Pricing Tiers", test_pricing),
        ("Mana Purchase", test_purchase),
        ("History", test_history),
        ("API Keys", test_api_keys),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n[ERROR] {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:8} | {name}")
    
    passed_count = sum(1 for _, p in results if p)
    print("-" * 60)
    print(f"Passed: {passed_count}/{len(results)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
