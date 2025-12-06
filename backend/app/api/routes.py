"""
API routes for QUBIC AEGIS
"""
import json
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
import requests
from app.services.mock_generator import QubicDataStream
from app.agents.orchestrator import AegisOrchestrator
from app.agents.multi_agent_orchestrator import MultiAgentOrchestrator
from app.models.events import RiskEvent
from app.config import settings

router = APIRouter()

# Global instances
# Use realistic simulation mode by default (can be disabled via QUBIC_REALISTIC_MODE=false)
data_stream = QubicDataStream(
    interval=settings.MOCK_DATA_INTERVAL,
    use_realistic_simulation=settings.QUBIC_REALISTIC_MODE
)
orchestrator = AegisOrchestrator()  # Legacy orchestrator for backward compatibility
multi_agent = MultiAgentOrchestrator()  # New multi-agent system

# WebSocket connections manager
class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending message: {e}")
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected WebSocket clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

# Background task for streaming data
stream_task = None

async def stream_transactions():
    """Background task that streams transactions to all connected WebSocket clients"""
    global data_stream, multi_agent
    print("🟢 Starting transaction stream...")
    try:
        async for transaction in data_stream.stream():
            try:
                # Use multi-agent orchestrator for comprehensive analysis
                analysis = await multi_agent.analyze_transaction(transaction)
                
                # Prepare message for frontend (handle both xai_summary and summary for compatibility)
                xai_explanation = analysis.get("xai_explanation", {})
                explanation_summary = xai_explanation.get("xai_summary") or xai_explanation.get("summary") or ""
                explanation_factors = xai_explanation.get("factors", [])
                
                # Prepare message for frontend
                message = {
                    "type": "transaction_analysis",
                    "data": {
                        "transaction": analysis["transaction"],
                        "risk_score": analysis["risk_analysis"]["risk_score"],
                        "risk_level": analysis["risk_analysis"]["risk_level"],
                        "explanation": explanation_summary,
                        "detailed_explanation": explanation_factors,
                        "risk_factors": analysis["risk_analysis"].get("risk_factors", []),
                        "prediction": analysis.get("prediction", {}),
                        "wallet_insights": analysis.get("wallet_insights", {}),
                        "market_intel": {
                            "token_symbol": transaction.token_symbol,
                            "token_stats": multi_agent.get_token_detail(transaction.token_symbol) if transaction.token_symbol else None,
                        } if transaction.token_symbol else None,
                        "defcon_status": analysis.get("defcon_status", {}),  # V2 BONUS: Adaptive thresholds
                        "sentiment_analysis": analysis.get("sentiment_analysis", {}),  # V2 BONUS: Sentiment
                    }
                }
                
                # V2 BONUS: Include active defense action in message if present
                if "automation_recommendation" in analysis and analysis["automation_recommendation"]:
                    automation = analysis["automation_recommendation"]
                    if isinstance(automation, dict) and automation.get("active_defense"):
                        message["data"]["active_defense"] = automation["active_defense"]
                
                # Broadcast to all connected clients
                if manager.active_connections:
                    await manager.broadcast(message)
                    print(f"📤 Broadcasted transaction Tick {transaction.tick} to {len(manager.active_connections)} clients")
                else:
                    print("⚠️ No active WebSocket connections, skipping broadcast")
                    
            except Exception as e:
                print(f"❌ Error analyzing transaction: {e}")
                import traceback
                traceback.print_exc()
    except Exception as e:
        print(f"❌ Error in stream_transactions: {e}")
        import traceback
        traceback.print_exc()

@router.websocket("/ws/monitor")
async def websocket_monitor(websocket: WebSocket):
    """
    WebSocket endpoint for real-time transaction monitoring
    Clients receive analyzed transaction data in real-time
    """
    global stream_task
    
    await manager.connect(websocket)
    
    try:
        # Start the streaming task if not already running
        if stream_task is None or stream_task.done():
            print("🚀 Starting new transaction stream task...")
            stream_task = asyncio.create_task(stream_transactions())
        else:
            print(f"✅ Stream task already running: {stream_task.done()}")
        
        # Send initial connection confirmation
        await manager.send_personal_message({
            "type": "connection",
            "status": "connected",
            "message": "Connected to QUBIC AEGIS monitoring stream"
        }, websocket)
        print(f"✅ WebSocket client connected. Total connections: {len(manager.active_connections)}")
        
        # Keep connection alive and handle client messages
        while True:
            try:
                # Wait for any message from client (ping/pong or commands)
                data = await websocket.receive_text()
                
                # Handle client commands if needed
                try:
                    command = json.loads(data)
                    if command.get("action") == "ping":
                        await manager.send_personal_message({
                            "type": "pong",
                            "timestamp": datetime.now().isoformat()
                        }, websocket)
                except json.JSONDecodeError:
                    pass  # Ignore non-JSON messages
                    
            except WebSocketDisconnect:
                manager.disconnect(websocket)
                break
                
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


class WebhookRequest(BaseModel):
    """Request model for webhook trigger (backward compatible)"""
    webhook_url: str
    message: str = "QUBIC AEGIS Alert: Suspicious transaction detected"

class RiskEventRequest(BaseModel):
    """Request model for RiskEvent-based automation trigger"""
    risk_event: Optional[Dict[str, Any]] = None  # RiskEvent dict (Pydantic model as dict)
    webhook_url: Optional[str] = None

@router.post("/api/trigger-automation")
async def trigger_automation(request: WebhookRequest):
    """
    Trigger automation webhook (for n8n integration)
    Generates dynamic attack scenarios for demo - different each time!
    """
    import random
    
    try:
        # Generate dynamic attack scenario (different each click!)
        attack_scenarios = [
            {
                "type": "Whale Dump Detected",
                "risk_score": random.randint(85, 95),
                "analysis": f"Massive sell order detected: {random.randint(500000, 2000000):,} QUBIC dumped in Block #{random.randint(8920, 8930)}. Market impact: -{random.randint(5, 15)}%",
            },
            {
                "type": "Flash Loan Exploit",
                "risk_score": random.randint(90, 99),
                "analysis": f"Abnormal liquidity withdrawal of {random.randint(1000000, 5000000):,} QUBIC detected. Re-entrancy pattern identified in Block #{random.randint(8920, 8930)}.",
            },
            {
                "type": "Smart Contract Re-entrancy",
                "risk_score": random.randint(95, 100),
                "analysis": f"Critical vulnerability detected: Re-entrancy attack pattern in contract 0x{random.randint(1000, 9999):x}... Multiple recursive calls identified.",
            },
            {
                "type": "Wash Trading Pattern",
                "risk_score": random.randint(75, 85),
                "analysis": f"Circular transaction pattern detected: {random.randint(50, 200)} self-transfers between {random.randint(3, 8)} wallets in last 10 blocks.",
            },
            {
                "type": "Liquidity Manipulation",
                "risk_score": random.randint(88, 96),
                "analysis": f"Coordinated liquidity drain detected: {random.randint(2, 5)} DEX pools affected. Price manipulation window: {random.randint(1, 3)} blocks.",
            },
        ]
        
        # Pick random scenario
        scenario = random.choice(attack_scenarios)
        risk_score = scenario["risk_score"]
        attack_type = scenario["type"]
        ai_analysis = scenario["analysis"]
        
        # Prepare rich payload for Discord embeds (format exact pour n8n)
        # Format simplifié que n8n peut facilement utiliser
        payload = {
            "body": {
                "risk_score": risk_score,
                "type": attack_type,
                "analysis": ai_analysis,
                "timestamp": datetime.now().isoformat(),
            }
        }
        
        # Send POST request to webhook
        response = requests.post(
            request.webhook_url,
            json=payload,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        response.raise_for_status()
        
        return {
            "status": "success",
            "message": "Webhook triggered successfully",
            "webhook_url": request.webhook_url,
            "response_status": response.status_code
        }
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to trigger webhook: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/api/trigger-automation-riskevent")
async def trigger_automation_riskevent(request: RiskEventRequest):
    """
    Trigger automation using RiskEvent model (new expert-level endpoint)
    
    Accepts a RiskEvent and processes it through the automator for n8n workflows
    """
    try:
        if not request.risk_event:
            raise HTTPException(status_code=400, detail="risk_event is required")
        
        # Create RiskEvent from dict
        risk_event = RiskEvent(**request.risk_event)
        
        # Process through automator
        automation_result = multi_agent.automator.process_risk_event(risk_event)
        
        # Trigger webhook if URL provided
        webhook_url = request.webhook_url or multi_agent.automator.default_webhook_url
        if webhook_url:
            webhook_result = multi_agent.automator.trigger_automation(
                webhook_url,
                automation_result["payload"]
            )
            automation_result["webhook_triggered"] = webhook_result
        
        return {
            "status": "success",
            "message": "RiskEvent processed successfully",
            "automation": automation_result,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "QUBIC AEGIS",
        "version": "2.0.0",
        "features": {
            "multi_agent": True,
            "predictive": True,
            "simulator": True,
            "xai": True,
        }
    }


# ==================== NEW ADVANCED ENDPOINTS ====================

class SimulationRequest(BaseModel):
    """Request model for attack simulation"""
    scenario_type: str
    parameters: dict = {}

@router.post("/api/simulate")
async def simulate_attack(request: SimulationRequest):
    """
    Simulate an attack scenario with step-by-step breakdown
    
    Available scenarios: whale_dump, wash_trade, flash_attack, wallet_drain, spam_attack, liquidity_manipulation
    
    Returns:
        {
            "scenario": scenario_type,
            "steps": [{tick, description, affected_wallets, risk_score}],
            "peak_risk": float,
            "estimated_impact": "Low|Medium|High|Critical",
            "aegis_recommendation": str (LLM-generated)
        }
    """
    try:
        result = await multi_agent.simulate_attack(request.scenario_type, request.parameters)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/predict")
async def get_predictions(horizon: str = "short_term", wallet_id: Optional[str] = None):
    """
    Get risk predictions
    
    Args:
        horizon: short_term (1h), medium_term (24h), long_term (7d)
        wallet_id: Optional wallet ID for per-wallet forecast
        
    Returns:
        Prediction data with history and forecast
    """
    try:
        if wallet_id:
            # Per-wallet forecast
            forecast = multi_agent.predictor.forecast(wallet_id)
            return forecast
        else:
            # Global prediction
            prediction = multi_agent.predictor.predict_risk(horizon)
            return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/wallet-graph")
async def get_wallet_graph(max_nodes: int = 50):
    """
    Get wallet interaction graph data with clustering
    
    Returns:
        {
            "nodes": [{id, label, role, risk_score}],
            "edges": [{source, target, weight}],
            "clusters": [{cluster_id, wallets, risk_level, description}]
        }
    """
    try:
        graph_data = multi_agent.get_wallet_graph(max_nodes)
        return graph_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ChatRequest(BaseModel):
    """Request model for AI chat"""
    message: str
    context: dict = {}

@router.post("/api/ask-aegis")
async def ask_aegis(request: ChatRequest):
    """
    Chat with Aegis AI - Ask questions about network security, risks, etc.
    Uses real Groq AI for intelligent responses
    """
    try:
        # Use AegisBrain for real AI chat if available
        if hasattr(multi_agent, 'ai_brain') and multi_agent.ai_brain:
            context = request.context or {}
            context.update({
                "recent_txs": len(multi_agent.transaction_history),
                "current_risk": 0,  # Can be enhanced with current risk calculation
            })
            
            ai_response = await multi_agent.ai_brain.chat(request.message, context)
            
            return {
                "answer": ai_response,
                "confidence": 0.90,
                "ai_generated": True,
            }
        else:
            # Fallback to rule-based responses
            message_lower = request.message.lower()
            
            if "whale" in message_lower or "large" in message_lower:
                response = {
                    "answer": "Whale activity detection uses volume thresholds and frequency analysis. Our system monitors transactions above 50,000 QUBIC and tracks wallet behavior patterns.",
                    "confidence": 0.85,
                    "sources": ["risk_analysis", "wallet_graph"],
                    "ai_generated": False,
                }
            elif "predict" in message_lower or "forecast" in message_lower:
                prediction = multi_agent.predictor.predict_risk("short_term")
                response = {
                    "answer": f"Based on current data, predicted risk is {prediction.get('predicted_risk', 0):.1f} with {prediction.get('confidence', 0):.1f}% confidence. Trend is {prediction.get('trend', 'stable')}.",
                    "confidence": prediction.get("confidence", 0) / 100,
                    "data": prediction,
                    "ai_generated": False,
                }
            elif "attack" in message_lower or "simulate" in message_lower:
                response = {
                    "answer": "I can simulate various attack scenarios including whale dumps, wash trading, flash loans, spam attacks, and liquidity manipulation. Use the /api/simulate endpoint or try asking about a specific scenario.",
                    "confidence": 0.90,
                    "available_scenarios": list(multi_agent.simulator.simulation_scenarios.keys()),
                    "ai_generated": False,
                }
            else:
                response = {
                    "answer": "I'm QUBIC AEGIS, your AI security copilot. I can help with risk analysis, predictions, attack simulations, and network security insights. Try asking about whales, predictions, or attack scenarios.",
                    "confidence": 0.80,
                    "ai_generated": False,
                }
            
            return response
    except Exception as e:
        return {
            "answer": f"Error generating response: {str(e)}",
            "confidence": 0.0,
            "ai_generated": False,
        }


@router.get("/api/wallet/{wallet_id}")
async def analyze_wallet(wallet_id: str):
    """
    Analyze a specific wallet
    """
    try:
        insights = multi_agent._get_wallet_insights(wallet_id)
        
        if not insights.get("exists"):
            raise HTTPException(status_code=404, detail="Wallet not found in current dataset")
        
        # Get behavior prediction
        wallet_txs = [
            tx for tx in multi_agent.transaction_history
            if tx.source_id == wallet_id or tx.dest_id == wallet_id
        ]
        wallet_features = multi_agent.collector.build_wallet_features(wallet_id, wallet_txs)
        behavior_prediction = multi_agent.predictor.predict_wallet_behavior(wallet_features, [])
        
        return {
            "wallet_id": wallet_id[:10] + "...",  # Anonymized
            "insights": insights,
            "features": wallet_features,
            "behavior_prediction": behavior_prediction,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# MARKET INTELLIGENCE ENDPOINTS
# ============================================

@router.get("/api/tokens")
async def get_tokens_overview():
    """
    Get AI-generated market intelligence overview for all tracked tokens.
    Returns token-level stats including risk scores, trends, and alerts.
    """
    try:
        return {
            "tokens": multi_agent.get_tokens_overview(),
            "generated_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tokens overview: {str(e)}")


@router.get("/api/tokens/{symbol}")
async def get_token_detail(symbol: str):
    """
    Get detailed market intelligence for a specific token.
    
    Args:
        symbol: Token symbol (e.g. "QX", "QXALPHA")
    
    Returns:
        TokenStats with risk metrics, trends, and alerts
    """
    try:
        token = multi_agent.get_token_detail(symbol)
        if not token:
            raise HTTPException(status_code=404, detail=f"Token '{symbol}' not tracked")
        return token
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching token detail: {str(e)}")


@router.get("/api/signals")
async def get_recent_signals(limit: int = 20):
    """
    Get recent AI-generated trading/security signals for Qubic tokens.
    
    Args:
        limit: Maximum number of signals to return (default: 20)
    
    Returns:
        List of TokenSignal objects with risk alerts and recommendations
    """
    try:
        return {
            "signals": multi_agent.get_recent_signals(limit=limit),
            "generated_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching signals: {str(e)}")


@router.get("/api/defcon-status")
async def get_defcon_status():
    """
    V2 BONUS: Get current DEFCON level and adaptive threshold status
    Returns the current security posture based on recent attack patterns.
    DEFCON 5 = Normal, DEFCON 1 = Maximum Alert (threshold lowered to 50).
    """
    defcon_status = multi_agent.adjust_sensitivity()
    return {
        "defcon_level": defcon_status["defcon_level"],
        "alert_threshold": defcon_status["alert_threshold"],
        "attacks_last_minute": defcon_status["attacks_last_minute"],
        "status": defcon_status["status"],
        "defcon_history": multi_agent.defcon_history[-10:] if hasattr(multi_agent, 'defcon_history') else [],  # Last 10 changes
        "description": "DEFCON level automatically adjusts based on attack frequency. "
                      "DEFCON 1 means >10 attacks/min detected - system is in maximum alert mode."
    }


@router.get("/api/market-intel/overview")
async def get_market_intel_overview():
    """
    Convenience endpoint returning both token overview and recent signals.
    Useful for dashboard widgets that need combined market intelligence.
    
    Returns:
        Combined tokens overview and recent signals
    """
    try:
        return {
            "tokens": multi_agent.get_tokens_overview(),
            "signals": multi_agent.get_recent_signals(limit=20),
            "generated_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market intel overview: {str(e)}")

