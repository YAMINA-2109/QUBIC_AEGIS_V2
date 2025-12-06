"""
Test script for V2 Market Intelligence
Verifies that tokens, signals, and market intel are working correctly
"""
import asyncio
import requests
import time
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL = "http://localhost:8000"


def wait_for_server(max_wait=30):
    """Wait for the server to be ready"""
    print("⏳ Waiting for server to start...")
    for i in range(max_wait):
        try:
            response = requests.get(f"{BASE_URL}/api/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
        if (i + 1) % 5 == 0:
            print(f"   Still waiting... ({i+1}s)")
    print("❌ Server did not start in time")
    return False


def test_market_intel_overview():
    """Test the /api/market-intel/overview endpoint"""
    print("\n📊 Testing /api/market-intel/overview...")
    try:
        response = requests.get(f"{BASE_URL}/api/market-intel/overview", timeout=10)
        if response.status_code == 200:
            data = response.json()
            tokens = data.get("tokens", [])
            signals = data.get("signals", [])
            
            print(f"✅ Market Intel Overview retrieved successfully")
            print(f"   📈 Tokens tracked: {len(tokens)}")
            print(f"   🚨 Signals generated: {len(signals)}")
            
            # Check if QXALPHA is being tracked
            qxalpha_tokens = [t for t in tokens if t.get("symbol") == "QXALPHA"]
            if qxalpha_tokens:
                qxalpha = qxalpha_tokens[0]
                print(f"\n   🎯 QXALPHA Stats:")
                print(f"      Risk Score: {qxalpha.get('latest_risk_score', 0):.2f}")
                print(f"      Trend: {qxalpha.get('trend', 'N/A')}")
                print(f"      Alerts 24h: {qxalpha.get('alerts_24h', 0)}")
            
            # Check signals
            if signals:
                print(f"\n   🔔 Recent Signals:")
                for signal in signals[:3]:  # Show first 3
                    print(f"      - {signal.get('token_symbol')}: {signal.get('signal_type')} (Risk: {signal.get('risk_level')})")
            
            return True
        else:
            print(f"❌ Error: Status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing market intel: {e}")
        return False


def test_tokens_endpoint():
    """Test the /api/tokens endpoint"""
    print("\n📋 Testing /api/tokens...")
    try:
        response = requests.get(f"{BASE_URL}/api/tokens", timeout=10)
        if response.status_code == 200:
            data = response.json()
            tokens = data.get("tokens", [])
            print(f"✅ Tokens endpoint working - {len(tokens)} tokens tracked")
            return True
        else:
            print(f"❌ Error: Status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_token_detail(symbol: str = "QXALPHA"):
    """Test the /api/tokens/{symbol} endpoint"""
    print(f"\n🔍 Testing /api/tokens/{symbol}...")
    try:
        response = requests.get(f"{BASE_URL}/api/tokens/{symbol}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Token detail retrieved:")
            print(f"   Symbol: {data.get('symbol')}")
            print(f"   Risk Score: {data.get('latest_risk_score', 0):.2f}")
            print(f"   Trend: {data.get('trend', 'N/A')}")
            return True
        elif response.status_code == 404:
            print(f"⚠️  Token {symbol} not yet tracked (wait a bit longer)")
            return False
        else:
            print(f"❌ Error: Status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_signals_endpoint():
    """Test the /api/signals endpoint"""
    print("\n🚨 Testing /api/signals...")
    try:
        response = requests.get(f"{BASE_URL}/api/signals?limit=10", timeout=10)
        if response.status_code == 200:
            data = response.json()
            signals = data.get("signals", [])
            print(f"✅ Signals endpoint working - {len(signals)} signals available")
            if signals:
                high_risk_signals = [s for s in signals if s.get("risk_level") in ("HIGH", "CRITICAL")]
                print(f"   High/Critical signals: {len(high_risk_signals)}")
            return True
        else:
            print(f"❌ Error: Status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 QUBIC AEGIS V2 Market Intelligence Verification")
    print("=" * 60)
    
    # Wait for server
    if not wait_for_server():
        print("\n❌ Cannot proceed without server. Make sure backend is running:")
        print("   cd backend && uvicorn main:app --reload")
        return False
    
    # Wait 5 seconds for transactions to accumulate
    print("\n⏳ Waiting 5 seconds for transactions to accumulate...")
    time.sleep(5)
    
    # Run tests
    results = []
    
    results.append(("Market Intel Overview", test_market_intel_overview()))
    results.append(("Tokens Endpoint", test_tokens_endpoint()))
    results.append(("Token Detail (QXALPHA)", test_token_detail("QXALPHA")))
    results.append(("Signals Endpoint", test_signals_endpoint()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {name}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! V2 Market Intelligence is working correctly!")
        return True
    elif passed > 0:
        print(f"\n⚠️  {passed}/{total} tests passed. Some features may need more transactions.")
        print("   Tip: Wait longer or check that transactions are being generated.")
        return False
    else:
        print("\n❌ No tests passed. Please check server logs and ensure transactions are being generated.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

