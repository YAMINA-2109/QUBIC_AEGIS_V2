"""
Multi-Agent Orchestrator - Coordinates all AI agents
The brain of QUBIC AEGIS
"""
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import uuid
from app.agents.agent_collector import AgentCollector
from app.agents.agent_predictor import AgentPredictor
from app.agents.agent_simulator import AgentSimulator
from app.agents.agent_automator import AgentAutomator
from app.agents.agent_risk_analyst import AgentRiskAnalyst
from app.core.ai_brain import AegisBrain
from app.models.transaction import Transaction
from app.models.events import RiskEvent
from app.services.market_intel import MarketIntelService
from app.models.market import TokenSignal


class MultiAgentOrchestrator:
    """
    Orchestrates all AI agents to provide comprehensive security analysis
    This is the core intelligence system
    """
    
    def __init__(self, rpc_url: Optional[str] = None, webhook_url: Optional[str] = None):
        """
        Initialize the multi-agent system
        
        Args:
            rpc_url: Qubic RPC endpoint
            webhook_url: Default n8n webhook URL
        """
        self.collector = AgentCollector(rpc_url)
        self.predictor = AgentPredictor()
        self.automator = AgentAutomator(webhook_url)
        self.risk_analyst = AgentRiskAnalyst()  # Real LLM-powered analyst
        
        # Try to initialize AegisBrain, fallback to risk_analyst if fails
        try:
            self.ai_brain = AegisBrain()
            if self.ai_brain.client is None:
                print("Warning: AegisBrain initialized but Groq client not available (no API key)")
        except Exception as e:
            print(f"Warning: Could not initialize AegisBrain: {e}")
            self.ai_brain = None
        
        # Initialize simulator with ai_brain if available (for LLM recommendations)
        self.simulator = AgentSimulator(ai_brain=self.ai_brain)
        
        # Market Intelligence service for token tracking
        self.market_intel = MarketIntelService()
        
        # Wallet interaction graph data - adjacency list for fast lookups
        self.wallet_graph_adjacency: Dict[str, Set[str]] = {}  # Adjacency list: wallet -> set of connected wallets
        self.wallet_graph: Dict[str, Dict[str, Any]] = {}  # Extended wallet data
        self.transaction_history: List[Transaction] = []
        
        # V2 BONUS: Adaptive Thresholds (DEFCON Mode)
        # Tracks recent high-risk events for adaptive sensitivity adjustment
        from collections import deque
        self.recent_high_risk_events: deque = deque(maxlen=100)  # Store timestamps of high-risk events
        self.current_defcon_level: int = 5  # DEFCON 5 = normal, DEFCON 1 = maximum alert
        self.adaptive_alert_threshold: float = 80.0  # Default threshold (will adjust based on DEFCON)
        self.defcon_history: List[Dict[str, Any]] = []  # Track DEFCON level changes
    
    def adjust_sensitivity(self) -> Dict[str, Any]:
        """
        V2 BONUS: Adaptive Thresholds - Auto-adapt sensitivity based on network conditions
        If attacks increase rapidly (>10 in 1min), enter DEFCON 1 mode (lower alert threshold)
        
        Returns:
            Dict with current DEFCON level and adjusted thresholds
        """
        from datetime import timedelta
        
        now = datetime.utcnow()
        one_minute_ago = now - timedelta(minutes=1)
        
        # Count high-risk events in last minute
        recent_events = [
            event_time for event_time in self.recent_high_risk_events 
            if event_time >= one_minute_ago
        ]
        attack_count = len(recent_events)
        
        # Determine DEFCON level based on attack frequency
        previous_defcon = self.current_defcon_level
        
        if attack_count >= 10:
            # DEFCON 1: Maximum alert - network under heavy attack
            self.current_defcon_level = 1
            self.adaptive_alert_threshold = 50.0  # Lower threshold (more sensitive)
        elif attack_count >= 5:
            # DEFCON 2: High alert
            self.current_defcon_level = 2
            self.adaptive_alert_threshold = 60.0
        elif attack_count >= 3:
            # DEFCON 3: Elevated alert
            self.current_defcon_level = 3
            self.adaptive_alert_threshold = 70.0
        elif attack_count >= 1:
            # DEFCON 4: Increased readiness
            self.current_defcon_level = 4
            self.adaptive_alert_threshold = 75.0
        else:
            # DEFCON 5: Normal operations
            self.current_defcon_level = 5
            self.adaptive_alert_threshold = 80.0  # Default threshold
        
        # Track DEFCON changes
        if previous_defcon != self.current_defcon_level:
            self.defcon_history.append({
                "timestamp": now.isoformat(),
                "previous_defcon": previous_defcon,
                "new_defcon": self.current_defcon_level,
                "attack_count_1min": attack_count,
                "threshold_adjusted": self.adaptive_alert_threshold,
                "reason": f"Attack frequency changed: {attack_count} attacks/min"
            })
            print(f"🚨 DEFCON Level Changed: {previous_defcon} → {self.current_defcon_level} (Alert threshold: {self.adaptive_alert_threshold})")
        
        return {
            "defcon_level": self.current_defcon_level,
            "alert_threshold": self.adaptive_alert_threshold,
            "attacks_last_minute": attack_count,
            "status": "DEFCON 1 - Maximum Alert" if self.current_defcon_level == 1 
                     else f"DEFCON {self.current_defcon_level} - Normal Operations" if self.current_defcon_level == 5
                     else f"DEFCON {self.current_defcon_level} - Elevated Alert"
        }
    
    async def analyze_transaction(self, transaction: Transaction) -> Dict[str, Any]:
        """
        Comprehensive transaction analysis using all agents
        V2: Now includes adaptive sensitivity adjustment and sentiment analysis
        
        Args:
            transaction: Transaction to analyze
            
        Returns:
            Complete analysis with predictions, explanations, and recommendations
        """
        # V2 BONUS: Adjust sensitivity based on recent attack patterns (DEFCON mode)
        defcon_status = self.adjust_sensitivity()
        
        # 1. Collect features
        features = self.collector.extract_features(transaction)
        
        # 2. Compute comprehensive risk score using enhanced Risk Engine
        wallet_insights = self._get_wallet_insights(transaction.source_id)
        
        # Prepare wallet history dict for risk scoring
        wallet_history = None
        if wallet_insights.get("exists"):
            # Calculate average amount from transaction history
            wallet_txs = [
                tx for tx in self.transaction_history
                if tx.source_id == transaction.source_id or tx.dest_id == transaction.source_id
            ]
            if wallet_txs:
                avg_amount = sum(tx.amount for tx in wallet_txs) / len(wallet_txs) if wallet_txs else 0
                wallet_history = {
                    "avg_amount": avg_amount,
                    "transaction_count": len(wallet_txs),
                    "total_volume": wallet_insights.get("total_volume", 0),
                }
        
        # 3. PRIORITÉ À L'IA : Si l'IA est disponible, on l'utilise comme décideur PRINCIPAL
        if self.ai_brain and self.ai_brain.client:
            # L'IA décide - On lui donne TOUT le contexte
            tx_data = {
                "source_id": transaction.source_id,
                "dest_id": transaction.dest_id,
                "amount": transaction.amount,
                "tick": transaction.tick,
                "type": transaction.type,
                "timestamp": transaction.timestamp.isoformat() if transaction.timestamp else None,
                "token_symbol": transaction.token_symbol,  # Ajout du token pour contexte IA
                "token_name": transaction.token_name,
            }
            
            # Contexte enrichi pour l'IA
            context = {
                "wallet_tx_count": wallet_insights.get("transaction_count", 0),
                "is_whale": wallet_insights.get("total_volume", 0) > 100000,
                "wallet_avg_amount": wallet_history.get("avg_amount", 0) if wallet_history else 0,
                "wallet_total_volume": wallet_insights.get("total_volume", 0),
                "features": features,  # Toutes les features extraites
            }
            
            # L'IA génère l'analyse complète
            ai_analysis = await self.ai_brain.analyze_transaction(tx_data, context)
            
            # On utilise l'analyse IA comme PRINCIPALE
            # V2 BONUS: Apply adaptive threshold (DEFCON mode adjusts sensitivity)
            base_risk_score = ai_analysis.get("risk_score", 0)
            base_risk_level = ai_analysis.get("risk_level", "LOW")
            
            # Adjust risk level based on DEFCON (if in high alert, upgrade risk level)
            adjusted_risk_score = base_risk_score
            adjusted_risk_level = base_risk_level
            if self.current_defcon_level <= 2 and base_risk_score >= self.adaptive_alert_threshold:
                # In DEFCON 1-2, upgrade risk levels
                if base_risk_level == "MEDIUM":
                    adjusted_risk_level = "HIGH"
                    adjusted_risk_score = min(100, base_risk_score + 10)
                elif base_risk_level == "HIGH":
                    adjusted_risk_level = "CRITICAL"
                    adjusted_risk_score = min(100, base_risk_score + 5)
            
            risk_analysis = {
                "risk_score": adjusted_risk_score,
                "risk_level": adjusted_risk_level,
                "threat_type": ai_analysis.get("anomaly_type") or ai_analysis.get("threat_type", "NORMAL"),
                "risk_factors": ai_analysis.get("risk_factors", []),
                "recommendation": ai_analysis.get("recommendation", "Monitor"),
                "analysis": ai_analysis.get("analysis", ""),
                "threat_description": ai_analysis.get("threat_description", ""),
                "confidence": ai_analysis.get("confidence", 95),  # Haute confiance car IA
                "ai_generated": True,  # Marqué comme généré par IA
                "defcon_adjusted": self.current_defcon_level < 5,  # Indicates if DEFCON affected this
                "defcon_level": self.current_defcon_level,  # Current DEFCON level
            }
            
        else:
            # Fallback: Si pas d'IA, utiliser rules + risk_analyst (moins puissant)
            comprehensive_risk = self.risk_analyst.compute_risk_score(
                transaction,
                features,
                wallet_history
            )
            
            # Essayer quand même risk_analyst (qui peut avoir Groq)
            ai_analysis = await self.risk_analyst.analyze(
                transaction,
                context={
                    "wallet_tx_count": wallet_insights.get("transaction_count", 0),
                    "is_whale": wallet_insights.get("total_volume", 0) > 100000,
                }
            )
            
            # Combiner (mais préférer l'IA si disponible)
            combined_risk_score = max(
                comprehensive_risk.get("risk_score", 0),
                ai_analysis.get("risk_score", 0)
            )
            
            risk_analysis = {
                "risk_score": combined_risk_score,
                "risk_level": comprehensive_risk.get("risk_level") or ai_analysis.get("risk_level", "LOW"),
                "threat_type": ai_analysis.get("anomaly_type") or ai_analysis.get("threat_type", "NORMAL"),
                "risk_factors": comprehensive_risk.get("factors", []) + ai_analysis.get("risk_factors", []),
                "recommendation": ai_analysis.get("recommendation", "Monitor"),
                "analysis": ai_analysis.get("analysis", ""),
                "threat_description": ai_analysis.get("threat_description", ""),
                "confidence": ai_analysis.get("confidence", 70),  # Moins de confiance sans IA principale
                "ai_generated": ai_analysis.get("ai_generated", False),
                "defcon_adjusted": self.current_defcon_level < 5,
                "defcon_level": self.current_defcon_level,
            }
            
            # V2 BONUS: Apply adaptive threshold in fallback mode too
            if self.current_defcon_level <= 2 and combined_risk_score >= self.adaptive_alert_threshold:
                if risk_analysis["risk_level"] == "MEDIUM":
                    risk_analysis["risk_level"] = "HIGH"
                    risk_analysis["risk_score"] = min(100, combined_risk_score + 10)
                elif risk_analysis["risk_level"] == "HIGH":
                    risk_analysis["risk_level"] = "CRITICAL"
                    risk_analysis["risk_score"] = min(100, combined_risk_score + 5)
        
        # V2 BONUS: Track high-risk events for adaptive sensitivity (DEFCON mode)
        if risk_analysis["risk_level"] in ("HIGH", "CRITICAL"):
            self.recent_high_risk_events.append(datetime.utcnow())
        
        # 4. Predict future risk (per-wallet)
        timestamp = transaction.timestamp or datetime.now()
        self.predictor.add_data_point(timestamp, risk_analysis["risk_score"], features)
        self.predictor.add_wallet_data_point(transaction.source_id, risk_analysis["risk_score"])
        
        # Get per-wallet forecast
        wallet_forecast = self.predictor.forecast(transaction.source_id)
        prediction = self.predictor.predict_risk("short_term")
        prediction["wallet_forecast"] = wallet_forecast
        
        # 5. Update wallet graph (adjacency list)
        self._update_wallet_graph(transaction)
        
        # 6. Generate systematic XAI explanation
        if self.ai_brain:
            xai_explanation = await self.ai_brain.explain_risk_decision(features, risk_analysis)
        else:
            xai_explanation = self._generate_xai_explanation(
                transaction,
                risk_analysis,
                features,
                prediction
            )
        
        # V2 BONUS: Sentiment Analysis (Mocked - correlates on-chain activity with social sentiment)
        sentiment_analysis = self._analyze_sentiment(transaction, risk_analysis)
        
        # 7. Create RiskEvent for automations
        risk_event = RiskEvent(
            wallet_id=transaction.source_id,
            risk_score=risk_analysis["risk_score"],
            risk_level=risk_analysis["risk_level"],
            category=self.risk_analyst.classify_priority(
                risk_analysis["risk_score"],
                prediction.get("predicted_risk")
            )["category"],
            tx_hash=transaction.signature,
            xai_summary=xai_explanation.get("summary", xai_explanation.get("xai_summary", "")),
            transaction_data={
                "source_id": transaction.source_id,
                "dest_id": transaction.dest_id,
                "amount": transaction.amount,
                "tick": transaction.tick,
                "type": transaction.type,
                "timestamp": transaction.timestamp.isoformat() if transaction.timestamp else None,
            },
            risk_factors=risk_analysis.get("risk_factors", []),
            prediction=prediction,
            recommendation=risk_analysis.get("recommendation", "Monitor")
        )
        
        # V2 BONUS: Generate automation with active defense for CRITICAL risks
        automation_recommendation = None
        if risk_analysis["risk_score"] > 70:
            # Process risk event through automator (includes active defense simulation)
            automation_payload = self.automator.process_risk_event(risk_event)
            automation_recommendation = automation_payload
        
        # 8. Update token-level market intelligence if token_symbol is present
        if transaction.token_symbol:
            token_symbol = transaction.token_symbol
            
            # Update token stats (result used by market intel system internally)
            _ = self.market_intel.update_token_from_event(
                token_symbol=token_symbol,
                risk_score=risk_analysis.get("risk_score", 0.0),
                risk_level=risk_analysis.get("risk_level", "LOW"),
                xai_summary=xai_explanation.get("xai_summary") if xai_explanation else None,
            )
            
            # If risk is HIGH or CRITICAL, create a TokenSignal
            if risk_analysis.get("risk_level") in ("HIGH", "CRITICAL"):
                signal = TokenSignal(
                    id=str(uuid.uuid4()),
                    token_symbol=token_symbol,
                    timestamp=datetime.utcnow(),
                    signal_type=risk_analysis.get("threat_type") or risk_analysis.get("category", "WHALE_DUMP_RISK"),
                    risk_score=risk_analysis.get("risk_score", 0.0),
                    risk_level=risk_analysis.get("risk_level", "HIGH"),
                    message=f"High risk event detected on {token_symbol}: {risk_analysis.get('analysis', 'Suspicious activity')}",
                    xai_summary=xai_explanation.get("xai_summary") if xai_explanation else None,
                )
                self.market_intel.add_signal(signal)
        
        return {
            "transaction": {
                "source_id": transaction.source_id,
                "dest_id": transaction.dest_id,
                "amount": transaction.amount,
                "tick": transaction.tick,
                "type": transaction.type,
                "timestamp": transaction.timestamp.isoformat() if transaction.timestamp else None,
            },
            "risk_analysis": risk_analysis,
            "prediction": prediction,
            "xai_explanation": xai_explanation,
            "wallet_insights": self._get_wallet_insights(transaction.source_id),
            "risk_event": risk_event.dict(),
            "automation_recommendation": automation_recommendation,
            "features": features,
            "defcon_status": defcon_status,  # V2 BONUS: Adaptive thresholds
            "sentiment_analysis": sentiment_analysis,  # V2 BONUS: Sentiment correlation
        }
    
    def _calculate_risk_score(self, tx: Transaction) -> Dict[str, Any]:
        """Calculate risk score with enhanced logic"""
        risk_score = 0
        risk_factors = []
        
        # Enhanced detection patterns
        if tx.amount > 50000:
            amount_risk = min(100, (tx.amount / 50000) * 30)
            risk_score += amount_risk
            risk_factors.append({
                "factor": "Large Amount",
                "severity": "high" if amount_risk > 50 else "medium",
                "details": f"Transaction amount ({tx.amount:,.2f}) exceeds normal threshold",
                "xai_reason": "Large transactions can indicate whale activity or potential market manipulation",
            })
        
        if tx.source_id == tx.dest_id:
            risk_score += 70
            risk_factors.append({
                "factor": "Wash Trading",
                "severity": "high",
                "details": "Source and destination are identical",
                "xai_reason": "Self-transfers often indicate wash trading, which artificially inflates volume",
            })
        
        # Check wallet history
        wallet_risk = self._assess_wallet_risk(tx.source_id)
        if wallet_risk["risk_score"] > 20:
            risk_score += wallet_risk["risk_score"] * 0.3
            risk_factors.extend(wallet_risk["factors"])
        
        risk_score = min(100, risk_score)
        
        risk_level = (
            "CRITICAL" if risk_score >= 70
            else "HIGH" if risk_score >= 40
            else "MEDIUM" if risk_score >= 20
            else "LOW"
        )
        
        return {
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "risk_factors": risk_factors,
        }
    
    def _assess_wallet_risk(self, wallet_id: str) -> Dict[str, Any]:
        """Assess risk based on wallet history"""
        wallet_txs = [tx for tx in self.transaction_history if tx.source_id == wallet_id or tx.dest_id == wallet_id]
        
        if len(wallet_txs) < 2:
            return {"risk_score": 0, "factors": []}
        
        factors = []
        risk_score = 0
        
        # High frequency
        if len(wallet_txs) > 50:
            risk_score += 15
            factors.append({
                "factor": "High Frequency Wallet",
                "severity": "medium",
                "details": f"Wallet has {len(wallet_txs)} recent transactions",
            })
        
        # Large total volume
        total_volume = sum(tx.amount for tx in wallet_txs if tx.source_id == wallet_id)
        if total_volume > 500000:
            risk_score += 20
            factors.append({
                "factor": "High Volume Wallet",
                "severity": "high",
                "details": f"Total volume: {total_volume:,.2f} QUBIC",
            })
        
        return {"risk_score": risk_score, "factors": factors}
    
    def _update_wallet_graph(self, transaction: Transaction):
        """Update wallet interaction graph"""
        source = transaction.source_id
        dest = transaction.dest_id
        
        # Update adjacency list
        if source not in self.wallet_graph_adjacency:
            self.wallet_graph_adjacency[source] = set()
        if dest not in self.wallet_graph_adjacency:
            self.wallet_graph_adjacency[dest] = set()
        
        self.wallet_graph_adjacency[source].add(dest)
        self.wallet_graph_adjacency[dest].add(source)
        
        # Update extended wallet data
        if source not in self.wallet_graph:
            self.wallet_graph[source] = {
                "id": source,
                "transactions": [],
                "counterparts": {},
                "total_volume": 0,
                "risk_score": 0,
                "role": "normal",
            }
        
        self.wallet_graph[source]["transactions"].append(transaction.tick)
        self.wallet_graph[source]["total_volume"] += transaction.amount
        
        if dest not in self.wallet_graph[source]["counterparts"]:
            self.wallet_graph[source]["counterparts"][dest] = 0
        self.wallet_graph[source]["counterparts"][dest] += 1
        
        # Update dest wallet
        if dest not in self.wallet_graph:
            self.wallet_graph[dest] = {
                "id": dest,
                "transactions": [],
                "counterparts": {},
                "total_volume": 0,
                "risk_score": 0,
                "role": "normal",
            }
        
        self.wallet_graph[dest]["transactions"].append(transaction.tick)
        if source not in self.wallet_graph[dest]["counterparts"]:
            self.wallet_graph[dest]["counterparts"][source] = 0
        self.wallet_graph[dest]["counterparts"][source] += 1
        
        # Keep history manageable
        self.transaction_history.append(transaction)
        if len(self.transaction_history) > 1000:
            self.transaction_history = self.transaction_history[-1000:]
    
    def _get_wallet_insights(self, wallet_id: str) -> Dict[str, Any]:
        """Get insights about a wallet"""
        if wallet_id not in self.wallet_graph:
            return {"exists": False}
        
        wallet_data = self.wallet_graph[wallet_id]
        return {
            "exists": True,
            "transaction_count": len(wallet_data["transactions"]),
            "total_volume": wallet_data["total_volume"],
            "unique_counterparts": len(wallet_data["counterparts"]),
            "top_counterparts": dict(
                sorted(wallet_data["counterparts"].items(), key=lambda x: x[1], reverse=True)[:5]
            ),
        }
    
    def _generate_xai_explanation(self, tx: Transaction, risk_analysis: Dict, features: Dict, prediction: Dict) -> Dict[str, Any]:
        """Generate Explainable AI explanation"""
        explanation_parts = []
        
        # Summary
        explanation_parts.append(
            f"Transaction analysis: {risk_analysis['risk_level']} risk (Score: {risk_analysis['risk_score']:.1f}/100)"
        )
        
        # Factors
        if risk_analysis["risk_factors"]:
            explanation_parts.append("\nDetected Risk Factors:")
            for factor in risk_analysis["risk_factors"]:
                explanation_parts.append(
                    f"  • {factor['factor']} ({factor['severity'].upper()}): {factor.get('xai_reason', factor['details'])}"
                )
        
        # Prediction
        if prediction.get("predicted_risk", 0) > 0:
            explanation_parts.append(
                f"\nPrediction: Risk is expected to be {prediction.get('predicted_risk', 0):.1f} in the near future "
                f"(Trend: {prediction.get('trend', 'stable')}, Confidence: {prediction.get('confidence', 0):.1f}%)"
            )
        
        return {
            "summary": explanation_parts[0],
            "detailed": "\n".join(explanation_parts),
            "confidence": prediction.get("confidence", 0),
        }
    
    async def simulate_attack(self, scenario_type: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """Simulate an attack scenario with step-by-step breakdown"""
        return await self.simulator.simulate(scenario_type, parameters)
    
    def get_wallet_graph(self, max_nodes: int = 50) -> Dict[str, Any]:
        """
        Get wallet interaction graph data with clustering
        
        Returns:
            {
                "nodes": [{id, label, role, risk_score}],
                "edges": [{source, target, weight}],
                "clusters": [cluster_data]
            }
        """
        # Limit nodes for performance - sort by volume
        top_wallets = sorted(
            self.wallet_graph.items(),
            key=lambda x: x[1]["total_volume"],
            reverse=True
        )[:max_nodes]
        
        nodes = []
        edges = []
        node_map = {}
        wallet_to_risk = {}  # Track risk scores per wallet
        
        # Build nodes
        for idx, (wallet_id, data) in enumerate(top_wallets):
            node_map[wallet_id] = idx
            
            # Determine role
            if data["total_volume"] > 100000:
                role = "whale"
            elif len(data["counterparts"]) > 20:
                role = "hub"
            elif data.get("risk_score", 0) > 70:
                role = "high_risk"
            else:
                role = "normal"
            
            nodes.append({
                "id": wallet_id,
                "label": wallet_id[:10] + "..." if len(wallet_id) > 10 else wallet_id,
                "role": role,
                "risk_score": data.get("risk_score", 0),
                "value": data["total_volume"],
            })
            wallet_to_risk[wallet_id] = data.get("risk_score", 0)
        
        # Build edges from adjacency list
        edge_counts = {}  # Track edge weights
        for wallet_id in node_map:
            if wallet_id in self.wallet_graph_adjacency:
                for connected_wallet in self.wallet_graph_adjacency[wallet_id]:
                    if connected_wallet in node_map:
                        # Create edge key (sorted for undirected graph)
                        edge_key = tuple(sorted([wallet_id, connected_wallet]))
                        if edge_key not in edge_counts:
                            edge_counts[edge_key] = 0
                        edge_counts[edge_key] += 1
        
        # Convert edge counts to edges
        for (source, target), weight in edge_counts.items():
            edges.append({
                "source": source,
                "target": target,
                "weight": weight,
            })
        
        # Simple clustering by risk level
        clusters = []
        high_risk_wallets = [w for w, risk in wallet_to_risk.items() if risk > 70]
        if high_risk_wallets:
            clusters.append({
                "cluster_id": "high_risk_cluster",
                "wallets": high_risk_wallets[:10],  # Limit to 10 for API response
                "risk_level": "HIGH",
                "description": "Cluster of high-risk wallets"
            })
        
        whale_wallets = [w for w, data in top_wallets if data["total_volume"] > 100000]
        if whale_wallets:
            clusters.append({
                "cluster_id": "whale_cluster",
                "wallets": whale_wallets[:10],
                "risk_level": "MEDIUM",
                "description": "Cluster of whale wallets"
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "clusters": clusters
        }
    
    def get_tokens_overview(self) -> List[Dict[str, Any]]:
        """Get overview of all tracked tokens"""
        return [t.dict() for t in self.market_intel.get_tokens_overview()]
    
    def get_token_detail(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get detailed stats for a specific token"""
        token = self.market_intel.get_token_by_symbol(symbol)
        return token.dict() if token else None
    
    def get_recent_signals(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent trading/security signals"""
        return [s.dict() for s in self.market_intel.get_recent_signals(limit=limit)]
    
    def _analyze_sentiment(
        self,
        transaction: Transaction,
        risk_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        V2 BONUS: Sentiment Analysis - Correlates on-chain activity with social sentiment
        Currently mocked, but structure is ready for real sentiment API integration
        
        Args:
            transaction: Transaction being analyzed
            risk_analysis: Risk analysis results
            
        Returns:
            Sentiment analysis with correlation score
        """
        import random
        
        # Mock sentiment data (simulates Twitter/Discord sentiment)
        # In production, this would call sentiment APIs or analyze social media feeds
        sentiment_score = random.uniform(-1.0, 1.0)  # -1 = negative, +1 = positive
        
        # Correlate with risk: High risk often correlates with negative sentiment
        if risk_analysis["risk_level"] in ("HIGH", "CRITICAL"):
            # High risk transactions often have negative sentiment (FUD, panic)
            sentiment_score = random.uniform(-0.8, -0.2)
        elif risk_analysis["risk_level"] == "MEDIUM":
            sentiment_score = random.uniform(-0.5, 0.3)
        else:
            sentiment_score = random.uniform(-0.2, 0.8)
        
        # Mock sentiment sources
        sentiment_sources = {
            "twitter_mentions": random.randint(10, 500) if risk_analysis["risk_score"] > 70 else random.randint(0, 50),
            "discord_messages": random.randint(5, 200) if risk_analysis["risk_score"] > 70 else random.randint(0, 30),
            "reddit_posts": random.randint(0, 50) if risk_analysis["risk_score"] > 70 else random.randint(0, 10),
        }
        
        # Determine sentiment label
        if sentiment_score > 0.5:
            sentiment_label = "BULLISH"
            correlation = "POSITIVE" if risk_analysis["risk_score"] < 50 else "DIVERGENT"
        elif sentiment_score < -0.5:
            sentiment_label = "BEARISH"
            correlation = "CONFIRMED" if risk_analysis["risk_score"] > 70 else "PARTIAL"
        else:
            sentiment_label = "NEUTRAL"
            correlation = "UNCERTAIN"
        
        return {
            "sentiment_score": round(sentiment_score, 2),  # -1.0 to 1.0
            "sentiment_label": sentiment_label,  # BULLISH, BEARISH, NEUTRAL
            "correlation_with_risk": correlation,  # CONFIRMED, PARTIAL, DIVERGENT, UNCERTAIN
            "social_mentions": sentiment_sources,
            "analysis": f"Social sentiment is {sentiment_label.lower()}. "
                       f"On-chain risk ({risk_analysis['risk_level']}) shows {correlation.lower()} correlation.",
            "note": "Mocked sentiment data. Ready for integration with Twitter/Discord/Reddit APIs."
        }
    
    def get_wallet_graph_data(self, max_nodes: int = 100) -> Dict[str, Any]:
        """Legacy method for backward compatibility"""
        graph = self.get_wallet_graph(max_nodes)
        # Convert to old format
        return {
            "nodes": [
                {
                    "id": n["id"][:10] + "..." if len(n["id"]) > 10 else n["id"],
                    "label": n["label"],
                    "value": n["value"],
                    "group": "high_risk" if n["risk_score"] > 70 else ("high_volume" if n["value"] > 100000 else "normal"),
                }
                for n in graph["nodes"]
            ],
            "links": [
                {
                    "source": e["source"],
                    "target": e["target"],
                    "value": e["weight"],
                }
                for e in graph["edges"]
            ]
        }

