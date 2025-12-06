"""
API Routes for QUBIC AEGIS (Expert Edition - FINAL)
Integrates Multi-Agent Orchestrator, Market Intelligence, and n8n Automation.
"""
import json
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
import requests
import random

# Import Expert Systems
from app.services.mock_generator import QubicDataStream
from app.agents.multi_agent_orchestrator import MultiAgentOrchestrator
from app.models.events import RiskEvent
from app.config import settings

router = APIRouter()

# --- INITIALIZATION ---
data_stream = QubicDataStream(
    interval=settings.MOCK_DATA_INTERVAL,
    use_realistic_simulation=True
)

# THE BRAIN: Expert Multi-Agent System
multi_agent = MultiAgentOrchestrator()

# --- WEBSOCKET MANAGER ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        # Copie la liste pour éviter les erreurs de modification pendant l'itération
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()
stream_task = None

# --- BACKGROUND STREAMING TASK ---
async def stream_transactions():
    print("🟢 Starting Aegis Neural Stream...")
    try:
        async for transaction in data_stream.stream():
            try:
                # 1. ANALYZE via Expert Agents
                analysis_result = await multi_agent.analyze_transaction(transaction)
                
                # 2. FORMAT for Frontend (React)
                risk_data = analysis_result["risk_analysis"]
                
                message = {
                    "type": "transaction_analysis",
                    "data": {
                        "transaction": analysis_result["transaction"],
                        "risk_score": risk_data["risk_score"],
                        "risk_level": risk_data["risk_level"],
                        "explanation": risk_data.get("reasoning", ""),
                        "risk_factors": risk_data.get("risk_factors", []),
                        "threat_type": risk_data.get("threat_type", "NORMAL"),
                        "prediction": analysis_result["prediction"],
                        "market_intel": {
                            "token_symbol": transaction.token_symbol,
                            "token_stats": multi_agent.get_token_detail(transaction.token_symbol) if transaction.token_symbol else None
                        } if transaction.token_symbol else None,
                        "defcon_status": analysis_result.get("defcon_status", {}),
                        "wallet_insights": analysis_result.get("wallet_insights", {})
                    }
                }
                
                await manager.broadcast(message)
            except Exception as e:
                print(f"⚠️ Stream Error (Skipping tx): {e}")
                
    except Exception as e:
        print(f"❌ Critical Stream Error: {e}")

@router.websocket("/ws/monitor")
async def websocket_monitor(websocket: WebSocket):
    global stream_task
    await manager.connect(websocket)
    
    if stream_task is None or stream_task.done():
        stream_task = asyncio.create_task(stream_transactions())
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- REST API ROUTES ---

class WebhookRequest(BaseModel):
    webhook_url: str
    scenario_type: Optional[str] = None

@router.post("/api/trigger-automation")
async def trigger_automation(request: WebhookRequest):
    """Simulates a SPECIFIC or RANDOM attack scenario"""
    try:
        # Define scenarios
        scenarios_map = {
            "WHALE": {"type": "Whale Dump Detected", "risk": 92, "msg": "Massive sell wall detected on QXALPHA. Wallet 0x89... dumping 5M tokens."},
            "RUG": {"type": "Rug Pull Initiated", "risk": 99, "msg": "CRITICAL: Deployer wallet removing 100% liquidity via unauthorized function call."},
            "FLASH": {"type": "Flash Loan Exploit", "risk": 95, "msg": "Abnormal liquidity withdrawal detected. Re-entrancy pattern identified."}
        }

        # Select Scenario
        if request.scenario_type and request.scenario_type in scenarios_map:
            scenario = scenarios_map[request.scenario_type]
        else:
            scenario = random.choice(list(scenarios_map.values()))
        
        # Payload for n8n
        payload = {
            "body": {
                "risk_score": scenario["risk"],
                "type": scenario["type"],
                "analysis": scenario["msg"],
                "timestamp": datetime.now().isoformat()
            }
        }
        
        requests.post(request.webhook_url, json=payload, timeout=5)
        return {"status": "success", "scenario": scenario["type"]}
        
    except Exception as e:
        # Just log error but don't crash frontend demo if n8n is down
        print(f"Automation trigger error: {e}")
        return {"status": "simulated", "message": "Automation triggered (Simulation mode)"}

# Market Intelligence Endpoints
@router.get("/api/market-intel/overview")
async def get_market_intel():
    return {
        "tokens": multi_agent.get_tokens_overview(),
        "signals": multi_agent.get_recent_signals()
    }

@router.get("/api/tokens/{symbol}")
async def get_token_detail(symbol: str):
    return multi_agent.get_token_detail(symbol)

@router.get("/api/signals")
async def get_signals():
    return {"signals": multi_agent.get_recent_signals()}

# Prediction Endpoint
@router.get("/api/predict")
async def get_prediction():
    return multi_agent.predictor.predict_risk("short_term")

# Wallet Graph Endpoint
@router.get("/api/wallet-graph")
async def get_wallet_graph(max_nodes: int = 50):
    return multi_agent.get_wallet_graph_data(max_nodes)

# Wallet Analysis Endpoint (Barre de recherche)
@router.get("/api/wallet/{wallet_id}")
async def analyze_wallet(wallet_id: str):
    return {
        "wallet_id": wallet_id,
        "risk_score": random.randint(10, 90), # Mock pour la démo si wallet inconnu
        "features": multi_agent._get_wallet_insights(wallet_id)
    }

# Simulation Endpoint
class SimRequest(BaseModel):
    scenario_type: str
    parameters: dict = {}

@router.post("/api/simulate")
async def simulate_attack(req: SimRequest):
    return await multi_agent.simulate_attack(req.scenario_type, req.parameters)

# Chat Endpoint
class ChatRequest(BaseModel):
    message: str

@router.post("/api/ask-aegis")
async def ask_aegis(req: ChatRequest):
    return {
        "answer": f"Aegis Analysis: I am monitoring {len(multi_agent.transaction_history)} transactions. System is stable. Ask me about specific wallets or tokens.",
        "confidence": 0.95
    }

# DEFCON Endpoint (Le manquant !)
@router.get("/api/defcon-status")
async def get_defcon_status():
    return multi_agent.adjust_sensitivity()

@router.get("/api/health")
def health():
    return {"status": "Aegis Online", "agents": 5, "mode": "EXPERT"}

# Network Emotion Endpoint
@router.get("/api/network-emotion")
async def get_network_emotion():
    return multi_agent.market_intel.get_network_emotion()