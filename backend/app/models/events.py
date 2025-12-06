"""
Risk Event models for automation and alerts
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class RiskEvent(BaseModel):
    """
    Risk event model for automations and alerts
    Represents a security risk event detected by AEGIS
    """
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique event identifier")
    wallet_id: str = Field(..., description="Wallet ID involved in the risk event")
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Risk score (0-100)")
    risk_level: str = Field(..., description="Risk level: LOW, MEDIUM, HIGH, or CRITICAL")
    category: str = Field(..., description="Event category (e.g., WHALE_DUMP, WASH_TRADING, FLASH_LOAN)")
    tx_hash: Optional[str] = Field(None, description="Transaction hash if applicable")
    xai_summary: Optional[str] = Field(None, description="Explainable AI summary of the risk")
    timestamp: datetime = Field(default_factory=datetime.now, description="Event timestamp")
    
    # Additional context
    transaction_data: Optional[Dict[str, Any]] = Field(None, description="Full transaction data")
    risk_factors: Optional[List[Dict[str, Any]]] = Field(None, description="List of risk factors")
    prediction: Optional[Dict[str, Any]] = Field(None, description="Future risk prediction if available")
    recommendation: Optional[str] = Field(None, description="Recommended action")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "550e8400-e29b-41d4-a716-446655440000",
                "wallet_id": "ABC123...",
                "risk_score": 85.5,
                "risk_level": "HIGH",
                "category": "WHALE_DUMP",
                "tx_hash": "0x1234...",
                "xai_summary": "Large transaction detected from known whale wallet",
                "timestamp": "2024-01-01T00:00:00",
                "recommendation": "Monitor closely"
            }
        }

