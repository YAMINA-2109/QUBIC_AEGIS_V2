import asyncio
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add backend directory to Python path FIRST (before imports)
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.agents.agent_collector import AgentCollector
from app.models.transaction import Transaction

async def test_expert_capabilities():
    print("TESTING AGENT COLLECTOR EXPERT MODE...\n")
    collector = AgentCollector()
    
    # ==========================================
    # TEST 1: BOT DETECTION
    # ==========================================
    print("Test 1: Simulation d'un BOT (Intervalles réguliers)...")
    base_time = datetime.now()
    bot_txs = []
    for i in range(10):
        tx = Transaction(
            source_id="BOT_WALLET_99",
            dest_id="EXCHANGE",
            amount=50,
            timestamp=base_time + timedelta(seconds=i*1.0),
            type="transfer",
            tick=1000+i,
            signature="sig_bot"
        )
        bot_txs.append(tx)
    
    results = await collector.process_batch(bot_txs)
    
    # Vérif Test 1
    if results and results[0].get('is_bot_probable'):
        print("   ✅ SUCCESS: Bot Detected via Math Entropy!\n")
    else:
        print("   ❌ FAILURE: Bot missed.\n")

    # ==========================================
    # CRUCIAL : ON VIDE LA MÉMOIRE AVANT LE TEST 2
    # ==========================================
    collector.transaction_buffer = [] 
    print("   (Buffer cleared for next test)\n")

    # ==========================================
    # TEST 2: DUSTING ATTACK
    # ==========================================
    print("🧪 Test 2: Simulation Dusting Attack...")
    dust_txs = []
    for i in range(10):
        tx = Transaction(
            source_id="HACKER_WALLET",
            dest_id=f"VICTIM_{i}",
            amount=0.00001, # Très petit montant
            timestamp=base_time,
            type="transfer",
            tick=2000,
            signature="sig_dust"
        )
        dust_txs.append(tx)
        
    results_dust = await collector.process_batch(dust_txs)
    
    # Vérif Test 2
    is_dusting = results_dust[0].get('is_dusting_attempt', False) if results_dust else False
    
    if is_dusting:
        print("   ✅ SUCCESS: Dusting Attack Pattern Recognized!")
        print("   -> AI Tag generated: ", results_dust[0].get('ai_tag'))
    else:
        print(f"   ❌ FAILURE: Dusting missed. (Flag is {is_dusting})")

    print("\n EXPERT COLLECTOR READY.")

if __name__ == "__main__":
    asyncio.run(test_expert_capabilities())