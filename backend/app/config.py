"""
Configuration management for QUBIC AEGIS (Hybrid Edition)
"""
import os
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""
    
    # --- API KEYS ---
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    
    # --- QUBIC NETWORK (REAL) ---
    # Liste des RPCs pour le Failover (Code du collègue)
    QUBIC_RPC_URLS: List[str] = [
        os.getenv("QUBIC_RPC_URL", "https://rpc.qubic.org/v1"),
        "https://testnet-rpc.qubic.org/v1",
        "https://rpc-staging.qubic.org/v2"
    ]
    
    # --- SIMULATION SETTINGS ---
    # Si True, on injecte des fausses attaques au milieu du trafic réel
    QUBIC_REALISTIC_MODE: bool = os.getenv("QUBIC_REALISTIC_MODE", "true").lower() == "true"
    MOCK_DATA_INTERVAL: float = float(os.getenv("MOCK_DATA_INTERVAL", "2.0"))
    
    # --- AUTOMATION (n8n) ---
    N8N_WEBHOOK_URL: Optional[str] = os.getenv(
        "N8N_WEBHOOK_URL",
        # Mets ton URL n8n qui marche ici par défaut pour être sûr
        "https://qubicaegis.app.n8n.cloud/webhook/b4662347-9dd7-4934-8eab-33bbcee20ddc"
    )
    
    # --- AI MODEL ---
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    AI_TEMPERATURE: float = 0.5
    
    # --- RISK ENGINE ---
    RISK_THRESHOLD_HIGH: float = 80.0
    RISK_WHALE_THRESHOLD: float = 500000.0
    
    # --- SERVER ---
    CORS_ORIGINS: list = ["*"]

settings = Settings()



# """
# Configuration management for QUBIC AEGIS
# Centralizes environment variables and settings
# """
# import os
# from typing import Optional
# from dotenv import load_dotenv

# load_dotenv()


# class Settings:
#     """Application settings loaded from environment variables"""
    
#     # API Keys
#     GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    
#     # Qubic Network
#     QUBIC_RPC_URL: Optional[str] = os.getenv("QUBIC_RPC_URL", "https://api.qubic.org")
    
#     # n8n Integration
#     N8N_WEBHOOK_URL: Optional[str] = os.getenv(
#         "N8N_WEBHOOK_URL",
#         "https://qubicaegis.app.n8n.cloud/webhook-test/b4662347-9dd7-4934-8eab-33bbcee20ddc"
#     )
    
#     # AI Model Configuration
#     GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
#     AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.7"))
    
#     # WebSocket Configuration
#     WEBSOCKET_HEARTBEAT_INTERVAL: int = int(os.getenv("WEBSOCKET_HEARTBEAT_INTERVAL", "30"))
    
#     # Risk Scoring
#     RISK_THRESHOLD_LOW: float = 30.0
#     RISK_THRESHOLD_MEDIUM: float = 70.0
#     RISK_THRESHOLD_HIGH: float = 90.0
    
#     # Risk Engine Configuration
#     RISK_BASELINE_AMOUNT: float = float(os.getenv("RISK_BASELINE_AMOUNT", "10000.0"))  # Baseline for amount comparison
#     RISK_ACTIVITY_WINDOW_MINUTES: int = int(os.getenv("RISK_ACTIVITY_WINDOW_MINUTES", "10"))  # Time window for activity
#     RISK_WHALE_THRESHOLD: float = float(os.getenv("RISK_WHALE_THRESHOLD", "50000.0"))  # Whale threshold
    
#     # Data Streaming
#     MOCK_DATA_INTERVAL: float = float(os.getenv("MOCK_DATA_INTERVAL", "2.0"))
#     QUBIC_REALISTIC_MODE: bool = os.getenv("QUBIC_REALISTIC_MODE", "true").lower() == "true"  # Realistic simulation mode
    
#     # CORS
#     CORS_ORIGINS: list = ["*"]  # to restrict in production


# # Global settings instance
# settings = Settings()

