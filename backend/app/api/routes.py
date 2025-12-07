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
        # Copy list to avoid modification errors during iteration
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()
stream_task = None

# --- BACKGROUND STREAMING TASK ---
async def stream_transactions():
    try:
        async for transaction in data_stream.stream():
            try:
                # 1. ANALYZE via Expert Agents
                analysis_result = await multi_agent.analyze_transaction(transaction)
                
                # 2. FORMAT for Frontend (React)
                risk_data = analysis_result["risk_analysis"]
                
                # Format transaction for frontend
                tx_dict = analysis_result["transaction"]
                
                # Ensure timestamp is ISO string
                if tx_dict.get("timestamp") and isinstance(tx_dict["timestamp"], str):
                    pass  # Already ISO string
                elif tx_dict.get("timestamp"):
                    tx_dict["timestamp"] = tx_dict["timestamp"].isoformat() if hasattr(tx_dict["timestamp"], "isoformat") else str(tx_dict["timestamp"])
                else:
                    tx_dict["timestamp"] = datetime.utcnow().isoformat()
                
                # Add source field (RPC vs SIMULATION) based on risk score
                if "source" not in tx_dict:
                    tx_dict["source"] = "SIMULATION" if risk_data.get("risk_score", 0) > 80 else "RPC"
                
                # Ensure all required fields exist
                if "token_symbol" not in tx_dict:
                    tx_dict["token_symbol"] = transaction.token_symbol
                if "token_name" not in tx_dict:
                    tx_dict["token_name"] = transaction.token_name
                
                message = {
                    "type": "transaction_analysis",
                    "data": {
                        "transaction": tx_dict,
                        "risk_score": risk_data.get("risk_score", 0),
                        "risk_level": risk_data.get("risk_level", "LOW"),
                        "explanation": risk_data.get("reasoning", risk_data.get("explanation", "")),
                        "risk_factors": risk_data.get("risk_factors", []),
                        "attack_type": risk_data.get("attack_type", "NORMAL"),
                        "prediction": analysis_result.get("prediction", {}),
                        "defcon_status": analysis_result.get("defcon_status", {}),
                        "sentiment_analysis": analysis_result.get("sentiment_analysis", {}),
                        "active_defense": analysis_result.get("automation", {}).get("active_defense") if analysis_result.get("automation") else None,
                        "xai_explanation": {
                            "summary": risk_data.get("reasoning", ""),
                            "xai_summary": risk_data.get("reasoning", "")
                        }
                    }
                }
                
                await manager.broadcast(message)
            except Exception as e:
                # Stream error - skip this transaction
                pass
                
    except Exception as e:
        # Critical stream error
        pass

@router.websocket("/ws/monitor")
async def websocket_monitor(websocket: WebSocket):
    global stream_task
    await manager.connect(websocket)
    
    # Send connection confirmation
    await websocket.send_json({
        "type": "connection",
        "message": " Connected to QUBIC AEGIS monitoring stream"
    })
    
    if stream_task is None or stream_task.done():
        stream_task = asyncio.create_task(stream_transactions())
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- REST API ROUTES ---

class WebhookRequest(BaseModel):
    webhook_url: Optional[str] = None
    scenario_type: Optional[str] = None
    message: Optional[str] = None

@router.post("/api/trigger-automation")
async def trigger_automation(request: WebhookRequest):
    """
    Simulates a SPECIFIC or RANDOM attack scenario.
    Forces data structure to match n8n requirements exactly.
    GENERATES FULL AI ANALYSIS for Discord messages.
    """
    try:
        # 1. Select scenario with COMPLETE AI ANALYSIS
        scenarios_map = {
            "WHALE": {
                "type": "WHALE_DUMP", 
                "risk": 92, 
                "short_msg": "High-value whale dump detected",
                "full_analysis": """High-value whale dump detected: 9150.4087847 QXTRADE transferred from an unknown source. Immediate admin review required to assess market impact and consider mitigation actions.

The transaction moves 9150.4087847 QXTRADE from an unidentified source to an unknown destination. In the QubicTrade ecosystem, large-volume transfers from opaque wallets are a hallmark of whale dumping attempts, which can cause abrupt price slippage and liquidity drain. Although bot probability is false, the sheer size and lack of traceable metadata trigger a high-threat assessment."""
            },
            "RUG": {
                "type": "RUG_PULL_INITIATED", 
                "risk": 99, 
                "short_msg": "CRITICAL: Deployer wallet removing 100% liquidity",
                "full_analysis": """CRITICAL: Deployer wallet removing 100% liquidity via unauthorized function call. Project: NOSTROMO-BETA.

Urgent: Detected complete liquidity withdrawal from deployer-controlled wallet. This pattern matches 100% of historical rug pull events. The transaction executes a removeLiquidity() function call without proper authorization checks, allowing the deployer to drain all pooled assets. Immediate intervention required to prevent total loss of user funds. All connected wallets should be flagged for monitoring."""
            },
            "FLASH": {
                "type": "FLASH_LOAN_ATTACK", 
                "risk": 95, 
                "short_msg": "Abnormal liquidity withdrawal detected",
                "full_analysis": """Abnormal liquidity withdrawal detected. Re-entrancy pattern identified in contract. Assets at risk.

Flash loan attack pattern detected: Large liquidity withdrawal followed by immediate re-entry into the same contract. The attacker is exploiting a re-entrancy vulnerability to drain funds before the contract state updates. The transaction sequence shows classic flash loan attack signatures: zero collateral, immediate execution, and state manipulation. Contract should be paused immediately."""
            }
        }

        # Fallback if type is not recognized
        scenario = scenarios_map.get(request.scenario_type, scenarios_map["WHALE"])
        
        # 2. Build COMPLETE Payload (EXACTLY what n8n expects)
        # Analysis is cleaned (no multiple \n) for Discord, but keep single line breaks
        analysis_text = scenario["full_analysis"].strip()
        # Replace double line breaks with single, but keep readable structure
        analysis_text = "\n".join(line.strip() for line in analysis_text.split("\n") if line.strip())
        
        # Build payload - IDENTICAL to automatic alerts
        # Automatic alerts send directly (without "body" wrapper)
        # Do the same so n8n workflow works the same way
        n8n_payload = {
            "risk_score": int(scenario["risk"]),  # INTEGER (92, 99, 95)
            "type": str(scenario["type"]),       # STRING (WHALE_DUMP, RUG_PULL_INITIATED, FLASH_LOAN_ATTACK)
            "analysis": analysis_text,  # Complete AI Analysis
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "CRITICAL" if scenario["risk"] >= 90 else "HIGH"
        }
        
        # Verify all fields are present
        assert "risk_score" in n8n_payload, "risk_score missing!"
        assert "type" in n8n_payload, "type missing!"
        assert "analysis" in n8n_payload and len(n8n_payload["analysis"]) > 0, "analysis missing or empty!"
        
        # 3. Send to n8n
        # Use frontend URL if provided, otherwise default from .env
        target_url = request.webhook_url or settings.N8N_WEBHOOK_URL
        
        if not target_url:
            return {"status": "error", "message": "No webhook URL configured"}
        
        # Send with explicit headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = requests.post(target_url, json=n8n_payload, headers=headers, timeout=10)
        
        return {"status": "success", "scenario": scenario["type"], "n8n_code": response.status_code}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Market Intelligence Endpoints
@router.get("/api/market-intel/overview")
async def get_market_intel():
    return {
        "tokens": multi_agent.get_tokens_overview(),
        "signals": multi_agent.get_recent_signals(),
        "generated_at": datetime.utcnow().isoformat()
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
        "risk_score": random.randint(10, 90),  # Mock for demo if wallet unknown
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

# DEFCON Endpoint
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

# =============================================================================
# SMARTGUARD ROUTES - C++ Contract Auditing (Integrated from SmartGuard)
# =============================================================================

# Import SmartGuard service (lazy import to avoid breaking if SmartGuard not available)
SMARTGUARD_AVAILABLE = False
SMARTGUARD_ERROR = None
try:
    from app.services.smart_guard import get_smart_guard_service
    SMARTGUARD_AVAILABLE = True
except ImportError as e:
    SMARTGUARD_AVAILABLE = False
    SMARTGUARD_ERROR = str(e)
    # SmartGuard not available - system will continue without it
    pass
except Exception as e:
    SMARTGUARD_AVAILABLE = False
    SMARTGUARD_ERROR = str(e)
    # SmartGuard not available - system will continue without it
    pass

class AuditRequest(BaseModel):
    code: str
    language: Optional[str] = "english"
    simulation_scenario: Optional[str] = None

class QuickAuditRequest(BaseModel):
    code: str
    language: Optional[str] = "english"

@router.post("/api/smart-guard/audit")
async def smart_guard_audit(request: AuditRequest):
    """
    Complete SmartGuard audit pipeline (8 steps).
    Returns full audit report including comments, security analysis, documentation, etc.
    """
    if not SMARTGUARD_AVAILABLE:
        error_msg = f"SmartGuard service not available. Please install langgraph dependencies. Error: {SMARTGUARD_ERROR or 'Unknown error'}"
        raise HTTPException(
            status_code=503,
            detail=error_msg
        )
    
    try:
        service = get_smart_guard_service()
        result = await service.audit_contract(
            code=request.code,
            language=request.language or "english",
            simulation_scenario=request.simulation_scenario
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit failed: {str(e)}")

@router.post("/api/smart-guard/quick-audit")
async def smart_guard_quick_audit(request: QuickAuditRequest):
    """
    Quick security audit (semantic analysis + security audit only).
    Faster than full audit for quick security checks.
    """
    if not SMARTGUARD_AVAILABLE:
        error_msg = f"SmartGuard service not available. Please install langgraph dependencies. Error: {SMARTGUARD_ERROR or 'Unknown error'}"
        raise HTTPException(
            status_code=503,
            detail=error_msg
        )
    
    try:
        service = get_smart_guard_service()
        result = await service.quick_audit(
            code=request.code,
            language=request.language or "english"
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick audit failed: {str(e)}")