import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.agent_automator import AgentAutomator

async def test_automation_logic():
    print(" TESTING AUTOMATOR AGENT (EASYCONNECT INTEGRATION)...\n")
    
    automator = AgentAutomator()
    
    # SCENARIO: Critical Rug Pull detected by Risk Analyst
    risk_event = {
        "attack_type": "RUG_PULL_INITIATED",
        "risk_level": "CRITICAL",
        "risk_score": 98,
        "reasoning": "Deployer wallet is removing 100% of liquidity via unauthorized function call."
    }
    
    print(f"Incoming Threat: {risk_event['attack_type']} (Score: {risk_event['risk_score']})")
    
    # Run Automator
    result = await automator.decide_and_execute(risk_event)
    
    decision = result.get('decision', {})
    execution = result.get('execution', {})
    
    print("\n" + "="*50)
    print(" 🛡️  DEFENSE PROTOCOL ACTIVATED")
    print("="*50)
    print(f"🧠 AI Decision:     {decision.get('protocol')}")
    print(f"📢 Action Message:  {decision.get('message')}")
    print(f"🚀 Execution:       {execution.get('status')} -> {execution.get('target')}")
    print("="*50 + "\n")
    
    # Validation
    protocol = decision.get('protocol')
    if protocol in ["NOTIFY_ADMIN_URGENT", "TRIGGER_CIRCUIT_BREAKER"]:
        print("SUCCESS: Automator chose a High-Severity response!")
    else:
        print(f"FAILURE: Response was too weak for a Critical threat ({protocol}).")

if __name__ == "__main__":
    asyncio.run(test_automation_logic())