"""
Aegis Orchestrator - Main AI agent for risk analysis
"""
from typing import Dict, Any
from app.models.transaction import Transaction


class AegisOrchestrator:
    """
    Orchestrates risk analysis for Qubic transactions
    Uses advanced rule-based analysis (to be enhanced with LLM later)
    """
    
    def __init__(self):
        """Initialize the orchestrator"""
        self.risk_thresholds = {
            "large_amount": 50000.0,  # Transactions above this are flagged
            "wash_trading": True,  # Flag self-transactions
            "rapid_transfer_min": 0.01,  # Suspiciously small amounts
            "rapid_transfer_max": 0.1,
        }
        self.transaction_history = {}  # Simple history for pattern detection
    
    def analyze_risk(self, tx: Transaction) -> Dict[str, Any]:
        """
        Analyze transaction risk and return score (0-100) with explanation
        
        Args:
            tx: Transaction to analyze
            
        Returns:
            Dictionary with risk_score (0-100), risk_level, and explanation
        """
        risk_score = 0
        risk_factors = []
        
        # Factor 1: Large amount detection
        if tx.amount > self.risk_thresholds["large_amount"]:
            amount_risk = min(100, (tx.amount / self.risk_thresholds["large_amount"]) * 30)
            risk_score += amount_risk
            risk_factors.append({
                "factor": "Large Amount",
                "severity": "high" if amount_risk > 50 else "medium",
                "details": f"Transaction amount ({tx.amount:,.2f}) exceeds normal threshold"
            })
        
        # Factor 2: Wash trading detection (self-transfer)
        if tx.source_id == tx.dest_id:
            risk_score += 70
            risk_factors.append({
                "factor": "Wash Trading",
                "severity": "high",
                "details": "Source and destination are identical (potential market manipulation)"
            })
        
        # Factor 3: Suspiciously small rapid transfers
        if self.risk_thresholds["rapid_transfer_min"] <= tx.amount <= self.risk_thresholds["rapid_transfer_max"]:
            risk_score += 40
            risk_factors.append({
                "factor": "Micro-Transaction Pattern",
                "severity": "medium",
                "details": "Unusually small amount detected (possible rapid transfer pattern)"
            })
        
        # Factor 4: Transaction type anomaly
        if tx.type != "transfer":
            risk_score += 30
            risk_factors.append({
                "factor": "Unusual Transaction Type",
                "severity": "medium",
                "details": f"Non-standard transaction type: {tx.type}"
            })
        
        # Factor 5: Pattern detection (same source making many transactions)
        if tx.source_id in self.transaction_history:
            self.transaction_history[tx.source_id] += 1
            if self.transaction_history[tx.source_id] > 10:
                risk_score += 25
                risk_factors.append({
                    "factor": "High Frequency",
                    "severity": "medium",
                    "details": f"Source account has made {self.transaction_history[tx.source_id]} transactions"
                })
        else:
            self.transaction_history[tx.source_id] = 1
        
        # Cap risk score at 100
        risk_score = min(100, risk_score)
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "CRITICAL"
        elif risk_score >= 40:
            risk_level = "HIGH"
        elif risk_score >= 20:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Build explanation
        explanation = self._build_explanation(risk_factors, risk_score, risk_level)
        
        return {
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "explanation": explanation,
            "risk_factors": risk_factors,
            "transaction": {
                "source_id": tx.source_id,
                "dest_id": tx.dest_id,
                "amount": tx.amount,
                "tick": tx.tick,
                "type": tx.type,
                "timestamp": tx.timestamp.isoformat() if tx.timestamp else None
            }
        }
    
    def _build_explanation(self, risk_factors: list, risk_score: float, risk_level: str) -> str:
        """Build a human-readable explanation of the risk analysis"""
        if not risk_factors:
            return "Transaction appears normal. No significant risk factors detected."
        
        explanation_parts = [f"Risk Level: {risk_level} (Score: {risk_score:.1f}/100)"]
        explanation_parts.append("\nRisk Factors Detected:")
        
        for i, factor in enumerate(risk_factors, 1):
            explanation_parts.append(
                f"{i}. {factor['factor']} ({factor['severity'].upper()}): {factor['details']}"
            )
        
        return "\n".join(explanation_parts)
    
    def reset_history(self):
        """Reset transaction history (useful for testing or periodic cleanup)"""
        self.transaction_history.clear()

