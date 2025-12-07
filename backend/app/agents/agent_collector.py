"""
Agent Data Collector (Hybrid Edition)
Combines:
1. Real Qubic RPC Data (from Teammate's Service)
2. Simulated Attacks (from Mock Generator)
3. Expert Intelligence (Entropy, AI Intent, Dusting detection)
"""
import os
import math
import asyncio
import logging
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime

# Models
from app.models.transaction import Transaction

# Services
from app.services.mock_generator import QubicDataStream 
from app.services.real_qubic_collector import QubicRPCCollector  # Le fichier qu'on vient de créer

# AI
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class AgentCollector:
    """
    The 'Eyes' of Aegis.
    Hybrid Engine: Ingests REAL data -> Injects SIMULATED threats -> Applies AI Logic.
    """
    
    def __init__(self, rpc_url: Optional[str] = None):
        # 1. Le Vrai Collecteur (Code du coéquipier)
        self.rpc_collector = QubicRPCCollector()
        
        # 2. Le Simulateur d'Attaque (Ton code pour la démo)
        # On l'utilise pour injecter des anomalies car le réseau réel est souvent calme
        self.simulator = QubicDataStream(use_realistic_simulation=True)
        
        # 3. L'Intelligence (Ton code Groq/Maths)
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = os.getenv("GROQ_MODEL")
        self.transaction_buffer: List[Transaction] = [] # Pour l'analyse d'entropie

    # --- PARTIE 1 : LA FUSION DES FLUX (HYBRID STREAM) ---
    
    async def stream_transactions(self):
        """
        Yields transactions from BOTH sources (Real + Sim).
        C'est ici que la magie opère.
        """
        sim_stream = self.simulator.stream()
        
        # Démarrer la session HTTP du collecteur réel
        async with self.rpc_collector as collector:
            while True:
                transactions_batch = []

                # A. Récupérer les VRAIES données (Priorité)
                try:
                    real_data_list = await collector.collect_latest_data()
                    for data in real_data_list:
                        # Conversion Dict -> Transaction Model
                        tx = Transaction(
                            source_id=data["source_address"],
                            dest_id=data["destination_address"],
                            amount=float(data["amount"]),
                            tick=int(data["tick_number"]),
                            type="transfer",
                            signature="real_net_sig", # Placeholder
                            timestamp=datetime.now(),
                            token_symbol="QUBIC", # Default for real net
                            is_anomaly=False
                        )
                        transactions_batch.append(tx)
                except Exception as e:
                    logger.warning(f"⚠️ RPC Sync warning: {e}")

                # B. Injecter une SIMULATION (si besoin pour la démo)
                # On injecte 1 simulation pour "pimenter" le flux réel
                try:
                    sim_tx = await anext(sim_stream)
                    # On marque visuellement que c'est une simu pour le dashboard (optionnel)
                    transactions_batch.append(sim_tx)
                except Exception:
                    pass

                # C. Appliquer ton INTELLIGENCE (Maths/AI) sur le lot mixte
                if transactions_batch:
                    # On utilise ta méthode process_batch existante !
                    enriched_batch = await self.process_batch(transactions_batch)
                    
                    # On "yield" les transactions une par une pour l'orchestrateur
                    # Mais on attache les features enrichies (entropie, ai_tag)
                    for i, tx in enumerate(transactions_batch):
                        # Petite astuce : on peut attacher les features à l'objet Transaction
                        # ou retourner un tuple. Pour simplifier ici, on renvoie l'objet.
                        yield tx

                await asyncio.sleep(2.0) # Rythme du heartbeat

    # --- PARTIE 2 : TON INTELLIGENCE EXISTANTE (Ne change pas) ---

    def calculate_entropy(self, timestamps: List[float]) -> float:
        # ... (Garde ton code exact ici)
        if len(timestamps) < 2: return 1.0
        deltas = np.diff(timestamps)
        if len(deltas) == 0 or np.sum(deltas) == 0: return 0.0
        return np.std(deltas) / np.mean(deltas) if np.mean(deltas) > 0 else 0

    def detect_dusting_attack(self, transactions: List[Transaction]) -> bool:
        # ... (Garde ton code exact ici)
        if not transactions: return False
        sources = [tx.source_id for tx in transactions]
        amounts = [tx.amount for tx in transactions]
        return len(set(sources)) == 1 and all(a < 1.0 for a in amounts) and len(transactions) > 5

    def enrich_with_ai_intent(self, tx: Transaction) -> Dict[str, str]:
        # ... (Garde ton code exact ici avec Groq)
        if tx.amount < 1000 and not tx.token_symbol:
            return {"ai_tag": "NOISE", "intent": "micro_transfer"}
        
        prompt = f"""
        Analyze Qubic TX: Amount: {tx.amount}, Type: {tx.type}.
        Classify intent: [WHALE_MOVE, CONTRACT_CALL, NORMAL]. Return category only.
        """
        try:
            completion = self.groq_client.chat.completions.create(
                model=self.model, messages=[{"role": "user", "content": prompt}], max_tokens=10
            )
            return {"ai_tag": completion.choices[0].message.content.strip()}
        except:
            return {"ai_tag": "UNKNOWN"}

    async def process_batch(self, new_txs: List[Transaction]) -> List[Dict[str, Any]]:
        """
        Ton processeur intelligent. Il s'applique maintenant aux données RÉELLES !
        """
        self.transaction_buffer.extend(new_txs)
        
        # Analyse Bot (Entropie) sur le vrai trafic + simulé
        timestamps = [t.timestamp.timestamp() for t in self.transaction_buffer if t.timestamp]
        bot_score = self.calculate_entropy(timestamps)
        is_bot = bot_score < 0.2
        
        # Analyse Dusting
        is_dusting = self.detect_dusting_attack(self.transaction_buffer)
        
        enriched_data = []
        for tx in new_txs:
            feats = self.extract_features(tx)
            feats["is_bot_probable"] = is_bot
            feats["is_dusting_attempt"] = is_dusting
            
            # Si c'est une grosse transaction réelle, l'IA l'analysera !
            if tx.amount > 10000 or is_dusting:
                feats.update(self.enrich_with_ai_intent(tx))
            
            enriched_data.append(feats)
            
        if len(self.transaction_buffer) > 50: self.transaction_buffer = []
        return enriched_data

    def extract_features(self, tx: Transaction) -> Dict[str, Any]:
        # ... (Garde ton code exact)
        return {
            "amount": tx.amount,
            "token": tx.token_symbol or "QUBIC",
            "is_anomaly": getattr(tx, "is_anomaly", False) # Pour savoir si c'est simulé
        }



# """
# Agent Data Collector (V2 - Expert Edition)
# Capabilities:
# - Real-time Qubic Data Ingestion (Mock/RPC Hybrid)
# - Mathematical Bot Detection (Entropy & Variance Analysis)
# - Semantic Intent Classification via Groq
# - Dusting Attack Pattern Recognition
# """
# import os
# import math
# import numpy as np
# from typing import Dict, Any, List, Optional
# from datetime import datetime, timedelta
# from app.models.transaction import Transaction

# # Integration IA
# from groq import Groq
# from dotenv import load_dotenv

# load_dotenv()

# class AgentCollector:
#     """
#     The 'Eyes' of Aegis.
#     Instead of just passing data, it pre-processes, tags, and enriches
#     transactions with behavioral metadata before the Risk Analyst sees them.
#     """
    
#     def __init__(self, rpc_url: Optional[str] = None):
#         self.rpc_url = rpc_url or "https://testnet.qubic.li/rpc"
        
#         # Init Groq for high-speed classification
#         self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
#         self.model = "llama3-70b-8192" # Ultra fast & smart
        
#         # Cache for batch analysis (to detect patterns like Dusting)
#         self.transaction_buffer: List[Transaction] = []
#         self.BATCH_WINDOW_SECONDS = 5 

#     def calculate_entropy(self, timestamps: List[float]) -> float:
#         """
#         Expert Math: Calculates time-delta entropy.
#         - Low Entropy (Regular intervals like 1.0s, 1.0s, 1.0s) = BOT
#         - High Entropy (Random intervals like 0.5s, 4.2s, 1.1s) = HUMAN
#         """
#         if len(timestamps) < 2:
#             return 1.0
        
#         deltas = np.diff(timestamps)
#         if len(deltas) == 0 or np.sum(deltas) == 0:
#             return 0.0
            
#         # Normalize stats
#         std_dev = np.std(deltas)
#         mean = np.mean(deltas)
        
#         # Coefficient of variation (CV)
#         # CV < 0.1 means extremely regular -> BOT
#         # CV > 1.0 means extremely random -> HUMAN
#         cv = std_dev / mean if mean > 0 else 0
#         return cv

#     def detect_dusting_attack(self, transactions: List[Transaction]) -> bool:
#         """
#         Detects if a single source is sending tiny amounts to many destinations rapidly.
#         """
#         if not transactions:
#             return False
            
#         sources = [tx.source_id for tx in transactions]
#         amounts = [tx.amount for tx in transactions]
        
#         # Logic: 1 Source -> Many Destinations + Tiny Amounts
#         unique_source = len(set(sources)) == 1
#         tiny_amounts = all(a < 1.0 for a in amounts) # Threshold for "Dust" in Qubic
#         high_volume = len(transactions) > 5 # In a short window
        
#         return unique_source and tiny_amounts and high_volume

#     def enrich_with_ai_intent(self, tx: Transaction) -> Dict[str, str]:
#         """
#         Uses Groq to classify the RAW intent based on metadata.
#         Only called for 'weird' transactions to save API credits/latency.
#         """
#         # Heuristic: Only ask AI if it looks suspicious or high value
#         if tx.amount < 1000 and not tx.token_symbol:
#             return {"ai_tag": "NOISE", "intent": "micro_transfer"}

#         prompt = f"""
#         You are a Data Forensic Expert on Qubic Blockchain.
#         Analyze this raw transaction metadata:
#         - Amount: {tx.amount} {tx.token_symbol or 'QUBIC'}
#         - Type: {tx.type}
#         - Source: {tx.source_id}
        
#         Classify the INTENT into one category:
#         [LIQUIDITY_ADD, WHALE_MOVEMENT, CONTRACT_DEPLOY, NORMAL_USER, EXCHANGE_DEPOSIT]
        
#         Return ONLY the category name.
#         """
        
#         try:
#             completion = self.groq_client.chat.completions.create(
#                 model=self.model,
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0.1,
#                 max_tokens=10
#             )
#             print("AI Intent: ", completion.choices[0].message.content.strip())
#             return {"ai_tag": completion.choices[0].message.content.strip(), "intent": "classified"}
#         except Exception:
#             return {"ai_tag": "UNKNOWN", "intent": "error"}

#     async def process_batch(self, new_txs: List[Transaction]) -> List[Dict[str, Any]]:
#         """
#         Process a batch of transactions together to find patterns.
#         """
#         enriched_data = []
        
#         # 1. Add to buffer
#         self.transaction_buffer.extend(new_txs)
        
#         # 2. Analyze Bot Behavior on the buffer timestamps
#         # Convert isoformat to timestamps for math
#         timestamps = [t.timestamp.timestamp() for t in self.transaction_buffer if t.timestamp]
#         bot_score = self.calculate_entropy(timestamps)
#         is_bot_probable = bot_score < 0.2 # Threshold for bot regularity
        
#         # 3. Analyze Dusting
#         is_dusting = self.detect_dusting_attack(self.transaction_buffer)
        
#         # 4. Enrich individual transactions
#         for tx in new_txs:
#             features = self.extract_features(tx)
            
#             # Inject Batch Intelligence
#             features["is_bot_probable"] = is_bot_probable
#             features["bot_regularity_score"] = round(bot_score, 2)
#             features["is_dusting_attempt"] = is_dusting
            
#             # Inject AI Intent (only for important ones)
#             if tx.amount > 10000 or is_dusting:
#                 ai_intent = self.enrich_with_ai_intent(tx)
#                 features.update(ai_intent)
#             else:
#                 features["ai_tag"] = "NORMAL_TRAFFIC"
                
#             enriched_data.append(features)
            
#         # Clear buffer (sliding window logic could be better but keep simple for hackathon)
#         if len(self.transaction_buffer) > 50:
#             self.transaction_buffer = []
            
#         return enriched_data

#     def extract_features(self, transaction: Transaction) -> Dict[str, Any]:
#         """
#         Base feature extraction + Qubic Specifics
#         """
#         amount_log = 0.0
#         if transaction.amount > 0:
#             try:
#                 amount_log = math.log2(transaction.amount)
#             except (ValueError, OverflowError):
#                 amount_log = 0.0
        
#         return {
#             "tx_hash": hash(f"{transaction.source_id}{transaction.timestamp}"),
#             "amount": transaction.amount,
#             "token": transaction.token_symbol or "QUBIC",
#             "amount_log": amount_log,
#             "timestamp": transaction.timestamp.isoformat(),
#             "source_id": transaction.source_id,
#             "dest_id": transaction.dest_id,
#             # Placeholder for the Risk Analyst to fill
#             "risk_score": None 
#         }