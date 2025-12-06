"""
Market Intelligence Models for QUBIC AEGIS
Token-level stats and trading signals
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TokenStats(BaseModel):
    """Statistics for a tracked Qubic token"""
    symbol: str = Field(..., description="Token symbol (e.g. QX, QXALPHA)")
    name: Optional[str] = Field(None, description="Human-readable name")
    last_updated: datetime = Field(..., description="Last time stats were updated")
    
    latest_risk_score: float = Field(..., description="Most recent aggregated risk score for this token (0–100)")
    average_risk_24h: float = Field(..., description="Average risk over last 24 hours (mocked if needed)")
    alerts_24h: int = Field(..., description="Number of high/critical events detected in last 24h")
    trend: str = Field(..., description="UP | DOWN | STABLE")
    
    # Optional simple meta-info for UI
    liquidity_tag: Optional[str] = Field(None, description="e.g. 'high_liquidity', 'low_liquidity', 'new_token'")
    risk_label: Optional[str] = Field(None, description="e.g. 'SAFE', 'WATCHLIST', 'HIGH_RISK'")


class TokenSignal(BaseModel):
    """Trading/security signal for a token"""
    id: str = Field(..., description="Unique signal identifier")
    token_symbol: str = Field(..., description="Token symbol this signal relates to")
    timestamp: datetime = Field(..., description="Signal creation time")
    
    signal_type: str = Field(..., description="e.g. 'WHALE_DUMP_RISK', 'VOLUME_SPIKE', 'SUSPICIOUS_CLUSTER'")
    risk_score: float = Field(..., description="Risk score at signal time (0–100)")
    risk_level: str = Field(..., description="LOW | MEDIUM | HIGH | CRITICAL")
    
    message: str = Field(..., description="Short human-readable description for traders")
    xai_summary: Optional[str] = Field(None, description="Optional AI explanation snippet")

