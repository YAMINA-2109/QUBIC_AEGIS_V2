import asyncio
import os
import sys

# Add project root to path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.agent_risk_analyst import AgentRiskAnalyst

async def test_risk_analysis():
    print("🧠 TESTING RISK ANALYST AGENT (LANGCHAIN + GROQ)...\n")
    
    analyst = AgentRiskAnalyst()
    
    # CASE 1: Simulating a dangerous WHALE DUMP on QubicTrade
    # These are mock features that would typically come from AgentCollector
    whale_data = {
        "source_id": "WHALE_WALLET_0x99",
        "dest_id": "QUBIC_TRADE_DEX",
        "amount": 5000000000, # Massive amount
        "token": "QXALPHA",   # Important Asset
        "is_bot_probable": True, # It's a bot
        "is_dusting_attempt": False,
        "ai_tag": "WHALE_MOVEMENT"
    }
    
    print(f"📉 SCENARIO 1: Analyzing Massive Whale Movement on DEX...")
    print(f"   Input: {whale_data['amount']} {whale_data['token']} from {whale_data['source_id']}")
    
    # Run Analysis
    result = await analyst.analyze(whale_data)
    
    # Display Report
    print("\n" + "="*40)
    print(" 🛡️  AEGIS SECURITY INTELLIGENCE REPORT")
    print("="*40)
    print(f"🚨 Risk Level:     {result.get('risk_level')}")
    print(f"📊 Risk Score:     {result.get('risk_score')}/100")
    print(f"👁️ Attack Type:    {result.get('attack_type')}")
    print(f"📝 Reasoning:      {result.get('reasoning')}")
    print(f"👉 Recommendation: {result.get('action_recommendation')}")
    print("="*40 + "\n")
    
    # Automated Verification
    score = result.get('risk_score', 0)
    if score > 70:
        print("✅ SUCCESS: The AI correctly identified the High Risk event!")
    else:
        print(f"❌ FAILURE: The AI underestimated the risk (Score: {score}).")

if __name__ == "__main__":
    asyncio.run(test_risk_analysis())