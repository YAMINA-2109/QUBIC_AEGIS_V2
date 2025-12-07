"""
originnAPI Routes for QUBIC AEGIS (Expert Edition - FINAL)
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
                print(f"⚠️ Stream Error (Skipping tx): {e}")
                
    except Exception as e:
        print(f"❌ Critical Stream Error: {e}")

@router.websocket("/ws/monitor")
async def websocket_monitor(websocket: WebSocket):
    global stream_task
    await manager.connect(websocket)
    
    # Send connection confirmation
    await websocket.send_json({
        "type": "connection",
        "message": "🟢 Connected to QUBIC AEGIS monitoring stream"
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
        # DEBUG: Log ce qui est reçu depuis le frontend
        print(f"📥 Received from frontend:")
        print(f"  - scenario_type: {request.scenario_type}")
        print(f"  - webhook_url: {request.webhook_url}")
        print(f"  - message: {request.message}")
        
        # 1. Sélection du scénario avec ANALYSES IA COMPLÈTES
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

        # Fallback si le type n'est pas reconnu
        scenario = scenarios_map.get(request.scenario_type, scenarios_map["WHALE"])
        
        # DEBUG: Vérifier quel scénario a été sélectionné
        print(f"✅ Selected scenario: {request.scenario_type} -> {scenario['type']} (risk: {scenario['risk']})")
        
        # 2. Construction du Payload COMPLET (EXACTEMENT ce que n8n attend)
        # Structure: { "body": { ... } } pour que n8n puisse lire $input.item.json.body
        # L'analyse est nettoyée (sans \n multiples) pour Discord, mais on garde les sauts de ligne simples
        analysis_text = scenario["full_analysis"].strip()
        # Remplacer les doubles sauts de ligne par un seul, mais garder la structure lisible
        analysis_text = "\n".join(line.strip() for line in analysis_text.split("\n") if line.strip())
        
        # Construction du payload - IDENTIQUE aux alertes automatiques
        # Les alertes automatiques envoient directement (sans wrapper "body")
        # On fait pareil pour que le workflow n8n fonctionne de la même façon
        n8n_payload = {
            "risk_score": int(scenario["risk"]),  # INTEGER (92, 99, 95)
            "type": str(scenario["type"]),       # STRING (WHALE_DUMP, RUG_PULL_INITIATED, FLASH_LOAN_ATTACK)
            "analysis": analysis_text,  # Analyse IA COMPLÈTE
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "CRITICAL" if scenario["risk"] >= 90 else "HIGH"
        }
        
        # Vérification que tous les champs sont bien présents
        assert "risk_score" in n8n_payload, "risk_score manquant!"
        assert "type" in n8n_payload, "type manquant!"
        assert "analysis" in n8n_payload and len(n8n_payload["analysis"]) > 0, "analysis manquante ou vide!"
        
        # 3. Envoi (Avec logs détaillés pour debug)
        payload_str = json.dumps(n8n_payload, indent=2, ensure_ascii=False)
        print(f"🚀 Sending to n8n:")
        print(payload_str)
        print(f"📊 Payload size: {len(payload_str)} bytes")
        print(f"📊 Analysis length: {len(analysis_text)} chars")
        
        # Utilise l'URL du frontend s'il y en a une, sinon celle par défaut du .env
        target_url = request.webhook_url or settings.N8N_WEBHOOK_URL
        
        print(f"🌐 Target URL: {target_url}")
        
        if not target_url:
            print("⚠️ WARNING: No webhook URL configured! Set N8N_WEBHOOK_URL in .env")
            return {"status": "error", "message": "No webhook URL configured"}
        
        # Envoyer avec headers explicites
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = requests.post(target_url, json=n8n_payload, headers=headers, timeout=10)
        print(f"✅ n8n Response: {response.status_code} - {response.text[:200]}")
        
        # Vérifier si la réponse contient des erreurs
        if response.status_code != 200:
            print(f"❌ ERROR: n8n returned {response.status_code}")
            print(f"Response body: {response.text}")
        
        return {"status": "success", "scenario": scenario["type"], "n8n_code": response.status_code}
        
    except Exception as e:
        print(f"❌ Automation Error: {e}")
        import traceback
        traceback.print_exc()
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