"""
Multi-Agent Orchestrator (V2 - Expert Edition)
Coordinates the 5 Expert Agents to provide comprehensive security analysis.
The Brain of QUBIC AEGIS.
"""
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque

# Import Expert Agents
from app.agents.agent_collector import AgentCollector
from app.agents.agent_risk_analyst import AgentRiskAnalyst
from app.agents.agent_predictor import AgentPredictor
from app.agents.agent_simulator import AgentSimulator
from app.agents.agent_automator import AgentAutomator

# Import Models & Services
from app.models.transaction import Transaction
from app.models.events import RiskEvent
from app.models.market import TokenSignal
from app.services.market_intel import MarketIntelService

class MultiAgentOrchestrator:
    """
    Central Nervous System of Aegis.
    It pipes data from one agent to another to build a complete Threat Intelligence report.
    """
    
    def __init__(self, rpc_url: Optional[str] = None):
        # 1. Initialize all Expert Agents
        self.collector = AgentCollector(rpc_url)
        self.risk_analyst = AgentRiskAnalyst() # LangChain + Groq
        self.predictor = AgentPredictor()      # Math + Groq
        self.simulator = AgentSimulator()      # Red Team AI
        self.automator = AgentAutomator()      # n8n + AI Decision
        
        # 2. Initialize Market Intelligence (In-Memory DB)
        self.market_intel = MarketIntelService()
        
        # 3. Initialize Graph Data (In-Memory)
        self.wallet_graph: Dict[str, Dict[str, Any]] = {} 
        self.transaction_history: List[Transaction] = []
        
        # 4. DEFCON System (Adaptive Thresholds)
        self.recent_high_risk_events = deque(maxlen=100)
        self.current_defcon_level = 5
        self.adaptive_alert_threshold = 80.0
        self.defcon_history = []

    async def analyze_transaction(self, transaction: Transaction) -> Dict[str, Any]:
        """
        The Main Pipeline: Data -> Analysis -> Prediction -> Action
        """
        # PHASE 0: DEFCON CHECK
        defcon_status = self.adjust_sensitivity()

        # PHASE 1: COLLECT (Enrichment)
        features = self.collector.extract_features(transaction)
        
        # PHASE 2: ANALYZE (The Judge)
        enriched_data = {
            **features,
            "is_bot_probable": False, 
            "ai_tag": "REAL_TIME_SCAN"
        }
        risk_analysis = await self.risk_analyst.analyze(enriched_data)
        
        # Apply DEFCON Sensitivity
        # If DEFCON 1 (Max Alert), boost risk scores
        if self.current_defcon_level <= 2:
            if risk_analysis.get("risk_score", 0) > 50:
                risk_analysis["risk_score"] = min(100, risk_analysis["risk_score"] + 10)
                risk_analysis["risk_level"] = "HIGH" if risk_analysis["risk_score"] > 70 else "MEDIUM"

        # Update DEFCON Trigger
        if risk_analysis.get("risk_level") in ["HIGH", "CRITICAL"]:
            self.recent_high_risk_events.append(datetime.utcnow())

        # PHASE 3: PREDICT (The Oracle)
        prediction = self.predictor.predict_future_risk(risk_analysis.get("risk_score", 0))
        
        # PHASE 4: UPDATE INTELLIGENCE (Graph & Market)
        self._update_graph(transaction, risk_analysis["risk_score"])
        self._update_market_intel(transaction, risk_analysis)

        # PHASE 5: AUTOMATE (The Bodyguard)
        automation_result = None
        if risk_analysis.get("risk_level") in ["HIGH", "CRITICAL"]:
            event = {
                "attack_type": risk_analysis.get("attack_type"),
                "risk_level": risk_analysis.get("risk_level"),
                "risk_score": risk_analysis.get("risk_score"),
                "reasoning": risk_analysis.get("reasoning")
            }
            automation_result = await self.automator.decide_and_execute(event)

        # FINAL REPORT
        # Convert transaction to dict and ensure timestamp is ISO string
        tx_dict = transaction.model_dump() if hasattr(transaction, "model_dump") else transaction.dict()
        
        # Ensure timestamp is ISO string format
        if tx_dict.get("timestamp"):
            if hasattr(tx_dict["timestamp"], "isoformat"):
                tx_dict["timestamp"] = tx_dict["timestamp"].isoformat()
            elif isinstance(tx_dict["timestamp"], str):
                pass  # Already a string
        else:
            tx_dict["timestamp"] = datetime.utcnow().isoformat()
        
        return {
            "transaction": tx_dict,
            "risk_analysis": risk_analysis,
            "prediction": prediction,
            "automation": automation_result,
            "defcon_status": defcon_status,
            "wallet_insights": {"exists": True, "transaction_count": len(self.transaction_history)} # Mocked for speed
        }

    def adjust_sensitivity(self) -> Dict[str, Any]:
        """Auto-adapt sensitivity based on network conditions"""
        now = datetime.utcnow()
        one_minute_ago = now - timedelta(minutes=1)
        recent_events = [t for t in self.recent_high_risk_events if t >= one_minute_ago]
        attack_count = len(recent_events)
        
        previous_defcon = self.current_defcon_level
        
        # Thresholds adjusted for demo: easier to trigger to show system in action
        if attack_count >= 3: self.current_defcon_level = 1  # DEFCON 1 with 3+ attacks/min (instead of 10)
        elif attack_count >= 2: self.current_defcon_level = 2  # DEFCON 2 with 2 attacks/min (instead of 5)
        elif attack_count >= 1: self.current_defcon_level = 3  # DEFCON 3 with 1 attack/min (instead of 3)
        else: self.current_defcon_level = 5
        
        # Adjust alert threshold based on DEFCON level
        if self.current_defcon_level == 1:
            self.adaptive_alert_threshold = 50.0
        elif self.current_defcon_level == 2:
            self.adaptive_alert_threshold = 60.0
        elif self.current_defcon_level == 3:
            self.adaptive_alert_threshold = 70.0
        else:
            self.adaptive_alert_threshold = 80.0
        
        return {
            "defcon_level": self.current_defcon_level,
            "alert_threshold": self.adaptive_alert_threshold,
            "attacks_last_minute": attack_count,
            "status": "MAXIMUM ALERT" if self.current_defcon_level == 1 else "NORMAL"
        }

    def _update_graph(self, tx: Transaction, risk_score: float):
        """Updates the internal wallet interaction graph"""
        source = tx.source_id
        dest = tx.dest_id
        
        if source not in self.wallet_graph:
            self.wallet_graph[source] = {"id": source, "risk_score": 0, "volume": 0, "connections": set()}
        if dest not in self.wallet_graph:
            self.wallet_graph[dest] = {"id": dest, "risk_score": 0, "volume": 0, "connections": set()}
            
        self.wallet_graph[source]["volume"] += tx.amount
        self.wallet_graph[source]["connections"].add(dest)
        self.wallet_graph[source]["risk_score"] = max(self.wallet_graph[source]["risk_score"], risk_score)

    def _update_market_intel(self, tx: Transaction, risk_analysis: Dict):
        """Updates token statistics"""
        if tx.token_symbol:
            self.market_intel.update_token_from_event(
                token_symbol=tx.token_symbol,
                risk_score=risk_analysis.get("risk_score", 0),
                risk_level=risk_analysis.get("risk_level", "LOW")
            )
            
            if risk_analysis.get("risk_level") in ["HIGH", "CRITICAL"]:
                signal = TokenSignal(
                    id=str(uuid.uuid4()),
                    token_symbol=tx.token_symbol,
                    timestamp=datetime.utcnow(),
                    signal_type=risk_analysis.get("attack_type", "ANOMALY"),
                    risk_score=risk_analysis.get("risk_score", 0),
                    risk_level=risk_analysis.get("risk_level"),
                    message=risk_analysis.get("reasoning", "Suspicious activity detected"),
                    xai_summary=f"Predicted trend: UP"
                )
                self.market_intel.add_signal(signal)

    # --- Helper methods for API Routes ---
    def _serialize_model(self, model):
        """Helper to serialize Pydantic models to dict with proper date formatting"""
        if model is None:
            return None
        if hasattr(model, "model_dump"):
            data = model.model_dump()
        elif hasattr(model, "dict"):
            data = model.dict()
        else:
            data = dict(model)
        
        # Convert datetime objects to ISO strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        
        return data
    
    def get_tokens_overview(self):
        tokens = self.market_intel.get_tokens_overview()
        return [self._serialize_model(t) for t in tokens]
        
    def get_recent_signals(self, limit=20):
        signals = self.market_intel.get_recent_signals(limit)
        return [self._serialize_model(s) for s in signals]
        
    def get_token_detail(self, symbol: str):
        token = self.market_intel.get_token_by_symbol(symbol)
        return self._serialize_model(token) if token else None
        
    def get_wallet_graph_data(self, max_nodes=50):
        nodes = []
        links = []
        seen_links = set()
        
        # Sort by volume to keep graph manageable
        sorted_wallets = sorted(self.wallet_graph.items(), key=lambda x: x[1]['volume'], reverse=True)[:max_nodes]
        wallet_ids = {w[0] for w in sorted_wallets}
        
        for wallet_id, data in sorted_wallets:
            nodes.append({
                "id": wallet_id,
                "label": wallet_id[:8]+"...",
                "val": data["volume"] / 1000, 
                "color": "#ef4444" if data["risk_score"] > 80 else "#22c55e"
            })
            for target in data["connections"]:
                if target in wallet_ids:
                    link_key = tuple(sorted([wallet_id, target]))
                    if link_key not in seen_links:
                        links.append({"source": wallet_id, "target": target})
                        seen_links.add(link_key)
                    
        return {"nodes": nodes, "links": links, "clusters": []}
    
    def _get_wallet_insights(self, wallet_id):
        # Fallback to avoid errors
        return {"exists": True, "transaction_count": 0}