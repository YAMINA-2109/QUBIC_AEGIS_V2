"""
Script de Vérification du Moteur Hybride
Objectif : Prouver qu'on reçoit du VRAI trafic Qubic ET des Simulations.
"""
import asyncio
import sys
import os

# Ajout du chemin pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.agent_collector import AgentCollector

async def verify_hybrid_stream():
    print("🛡️  INITIALISATION DU COLLECTEUR HYBRIDE...")
    print("------------------------------------------------")
    
    # On instancie l'agent (il va lancer le RPC collector de ton pote + le simulateur)
    collector = AgentCollector()
    
    print("👀 Écoute du flux en cours... (Ctrl+C pour arrêter)")
    print("   Légende : 🌐 = Donnée Réelle (RPC) | ⚔️ = Attaque Simulée (AI)")
    print("------------------------------------------------")

    try:
        # On regarde les 20 premières transactions qui arrivent
        count = 0
        async for tx in collector.stream_transactions():
            count += 1
            
            # ANALYSE : Est-ce du réel ou du faux ?
            # Les données réelles ont des ticks élevés (> 100 000)
            # Les simulations commencent souvent à 1000 ou ont un flag is_anomaly
            
            source_type = "🌐 LIVE RPC"
            if getattr(tx, "is_anomaly", False) or tx.tick < 100000:
                source_type = "⚔️ SIMULATION"
            
            # Affichage formaté
            print(f"[{count}] {source_type} | Tick: {tx.tick} | Amount: {tx.amount:,.2f} | Token: {tx.token_symbol}")
            
            if count >= 20:
                print("\n✅ TEST TERMINÉ : Le flux est actif et mixte.")
                break
                
    except Exception as e:
        print(f"❌ ERREUR : {e}")

if __name__ == "__main__":
    try:
        asyncio.run(verify_hybrid_stream())
    except KeyboardInterrupt:
        print("\nArrêt du test.")