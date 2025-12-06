"""
Configuration management for QUBIC AEGIS
Centralizes environment variables and settings
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""
    
    # API Keys
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    
    # Qubic Network
    QUBIC_RPC_URL: Optional[str] = os.getenv("QUBIC_RPC_URL", "https://api.qubic.org")
    
    # n8n Integration
    N8N_WEBHOOK_URL: Optional[str] = os.getenv(
        "N8N_WEBHOOK_URL",
        "https://qubicaegis.app.n8n.cloud/webhook-test/bc96d8cb-43f8-4447-9fc9-d93abc18e4b0"
    )
    
    # AI Model Configuration
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.7"))
    
    # WebSocket Configuration
    WEBSOCKET_HEARTBEAT_INTERVAL: int = int(os.getenv("WEBSOCKET_HEARTBEAT_INTERVAL", "30"))
    
    # Risk Scoring
    RISK_THRESHOLD_LOW: float = 30.0
    RISK_THRESHOLD_MEDIUM: float = 70.0
    RISK_THRESHOLD_HIGH: float = 90.0
    
    # Risk Engine Configuration
    RISK_BASELINE_AMOUNT: float = float(os.getenv("RISK_BASELINE_AMOUNT", "10000.0"))  # Baseline for amount comparison
    RISK_ACTIVITY_WINDOW_MINUTES: int = int(os.getenv("RISK_ACTIVITY_WINDOW_MINUTES", "10"))  # Time window for activity
    RISK_WHALE_THRESHOLD: float = float(os.getenv("RISK_WHALE_THRESHOLD", "50000.0"))  # Whale threshold
    
    # Data Streaming
    MOCK_DATA_INTERVAL: float = float(os.getenv("MOCK_DATA_INTERVAL", "2.0"))
    QUBIC_REALISTIC_MODE: bool = os.getenv("QUBIC_REALISTIC_MODE", "true").lower() == "true"  # Realistic simulation mode
    
    # CORS
    CORS_ORIGINS: list = ["*"]  # to restrict in production


# Global settings instance
settings = Settings()

