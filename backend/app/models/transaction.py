"""
Transaction model for Qubic blockchain transactions
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Transaction(BaseModel):
    """Represents a Qubic blockchain transaction"""
    source_id: str = Field(..., description="Source account ID")
    dest_id: str = Field(..., description="Destination account ID")
    amount: float = Field(..., description="Transaction amount in Qubic units")
    tick: int = Field(..., description="Block tick number")
    type: str = Field(default="transfer", description="Transaction type")
    signature: str = Field(..., description="Transaction signature")
    timestamp: Optional[datetime] = Field(default=None, description="Transaction timestamp")
    is_anomaly: Optional[bool] = Field(default=False, description="Flag for anomaly detection")
    token_symbol: Optional[str] = Field(default=None, description="Token symbol traded on Qubic (e.g. QX, QXALPHA)")
    token_name: Optional[str] = Field(default=None, description="Human-readable token name if available")

    class Config:
        json_schema_extra = {
            "example": {
                "source_id": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
                "dest_id": "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
                "amount": 1000.5,
                "tick": 12345,
                "type": "transfer",
                "signature": "signature_hash_here",
                "timestamp": "2024-01-01T00:00:00",
                "is_anomaly": False,
                "token_symbol": "QXALPHA",
                "token_name": "Qubic Alpha Token"
            }
        }

