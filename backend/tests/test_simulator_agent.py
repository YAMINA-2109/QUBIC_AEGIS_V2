import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.agent_simulator import AgentSimulator

async def test_war_games():
    print("🎮 TESTING SIMULATOR AGENT (RED TEAM MODE)...\n")
    
    simulator = AgentSimulator()
    
    token = "QXALPHA"
    attack = "Liquidity Draining (Flash Loan)"
    liquidity = 10_000_000 # 10 Million QUBIC
    
    print(f"⚔️  Running Simulation: {attack} on {token}...")
    print(f"💰 Target Liquidity: {liquidity} QUBIC")
    
    # Run the simulation
    result = await simulator.run_simulation(token, attack, liquidity)
    
    print("\n" + "="*50)
    print(f" 💀 ATTACK SIMULATION REPORT: {result.get('simulation_id')}")
    print("="*50)
    print(f"🎯 Probability of Success: {result.get('success_probability')}%")
    print(f"💸 Estimated Loss:         {result.get('estimated_loss')} QUBIC")
    print("\n🪜 Kill Chain (Attack Steps):")
    
    steps = result.get('steps', [])
    for i, step in enumerate(steps):
        print(f"   {i+1}. {step}")
        
    print(f"\n🛡️ Mitigation: {result.get('mitigation')}")
    print("="*50 + "\n")
    
    # Validation
    if result.get('success_probability') is not None:
        print("✅ SUCCESS: Simulation generated a valid war-game scenario!")
    else:
        print("❌ FAILURE: Simulation failed.")

if __name__ == "__main__":
    asyncio.run(test_war_games())