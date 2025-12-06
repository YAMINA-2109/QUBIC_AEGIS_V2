"""
Agent Risk Analyst - Real LLM-powered Risk Analysis
Uses Groq for fast, intelligent analysis
Enhanced with comprehensive risk scoring and auto-triage
"""
from typing import Dict, Any, Optional, List
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

from app.models.transaction import Transaction
from app.config import settings

# Import Groq with error handling for version compatibility
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("WARNING: groq package not available. Risk analysis will use fallback rules.")


class AgentRiskAnalyst:
    """
    Real AI-powered risk analyst using Groq LLM
    Generates unique, intelligent analysis for each transaction
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the risk analyst with Groq client
        
        Args:
            api_key: Groq API key (or from env GROQ_API_KEY)
        """
        if not GROQ_AVAILABLE:
            print("WARNING: groq package not available. Risk analysis will use fallback rules.")
            self.client = None
            return
            
        # Load environment variables again (in case .env wasn't loaded earlier)
        load_dotenv()
        
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            print("WARNING: GROQ_API_KEY not found in environment variables.")
            # Try to load from common locations
            env_locations = [
                Path(__file__).parent.parent.parent / '.env',  # backend/.env
                Path(__file__).parent.parent.parent.parent / '.env',  # root/.env
                Path.cwd() / '.env',  # current directory
                Path.cwd().parent / '.env',  # parent directory
            ]
            for loc in env_locations:
                if loc.exists():
                    print(f"DEBUG: Found .env at: {loc}")
                    load_dotenv(dotenv_path=loc)
                    self.api_key = os.getenv("GROQ_API_KEY")
                    if self.api_key:
                        print(f"✅ Loaded GROQ_API_KEY from: {loc}")
                        break
            
            if not self.api_key:
                print("Risk analysis will use fallback rules (no AI).")
                self.client = None
                return
        else:
            try:
                # Try to initialize Groq client
                self.client = Groq(api_key=self.api_key)
            except (TypeError, AttributeError) as e:
                # Handle version compatibility issues
                print(f"WARNING: Groq initialization error (possible version issue): {e}")
                print("Risk analysis will use fallback rules. Please check groq package version.")
                self.client = None
            except Exception as e:
                print(f"WARNING: Failed to initialize Groq client: {e}")
                print("Risk analysis will use fallback rules.")
                self.client = None
        
        # Cache for similar transactions to reduce API calls
        self.analysis_cache: Dict[str, Dict] = {}
        
        # Wallet activity tracking for risk scoring
        self.wallet_activity: Dict[str, List[datetime]] = {}
        self.wallet_history: Dict[str, List[Dict[str, Any]]] = {}  # Historical averages per wallet
    
    async def analyze(self, transaction: Transaction, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze transaction using real LLM
        
        Args:
            transaction: Transaction to analyze
            context: Optional additional context (wallet history, etc.)
            
        Returns:
            AI-generated risk analysis
        """
        if not self.client:
            return self._fallback_analysis(transaction)
        
        try:
            # Prepare transaction data for LLM
            tx_data = {
                "source_id": transaction.source_id[:10] + "...",  # Anonymized
                "dest_id": transaction.dest_id[:10] + "...",
                "amount": transaction.amount,
                "tick": transaction.tick,
                "type": transaction.type,
                "timestamp": transaction.timestamp.isoformat() if transaction.timestamp else None,
            }
            
            # Build prompt
            prompt = self._build_analysis_prompt(tx_data, context)
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Fast and intelligent
                messages=[
                    {
                        "role": "system",
                        "content": "You are QUBIC AEGIS, an expert AI security analyst for the Qubic blockchain. You analyze transactions for security risks, anomalies, and potential attacks. You respond in a concise, technical format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,  # More precise for security analysis
                max_tokens=700,  # More tokens for detailed analysis
            )
            
            # Parse LLM response
            ai_response = response.choices[0].message.content
            return self._parse_ai_response(ai_response, transaction)
            
        except Exception as e:
            print(f"Error in LLM analysis: {e}")
            return self._fallback_analysis(transaction)
    
    def _build_analysis_prompt(self, tx_data: Dict, context: Optional[Dict]) -> str:
        """Build enhanced prompt for stronger AI analysis"""
        prompt = f"""Analyze this Qubic blockchain transaction with INTELLIGENCE and EXPERTISE:

Transaction Data:
- Source: {tx_data['source_id']}
- Destination: {tx_data['dest_id']}
- Amount: {tx_data['amount']:,.2f} QUBIC
- Type: {tx_data['type']}
- Block Tick: {tx_data['tick']}
"""
        
        if context:
            prompt += "\nENRICHED CONTEXT (use this for intelligent analysis):\n"
            prompt += f"- Wallet transaction history: {context.get('wallet_tx_count', 0)} previous transactions\n"
            if context.get('is_whale'):
                prompt += "- ⚠️ WHALE WALLET - Market manipulation potential\n"
            if context.get('wallet_avg_amount'):
                current_amount = tx_data['amount']
                avg_amount = context.get('wallet_avg_amount', 1)
                if avg_amount > 0:
                    deviation = abs(current_amount - avg_amount) / avg_amount * 100
                    prompt += f"- Amount deviation from wallet average: {deviation:.1f}% {'(SUSPICIOUS)' if deviation > 200 else '(normal)'}\n"
        
        prompt += """
ANALYSIS INSTRUCTIONS (be intelligent, not just rule-based):

1. BEHAVIORAL ANALYSIS:
   - Compare this amount with wallet's historical patterns (if available)
   - Detect suspicious patterns: self-transfers, rapid sequences, unusual amounts
   - Identify manipulation attempts: wash trading, pump & dump, coordinated attacks

2. SECURITY ANALYSIS:
   - Detect potential attacks: flash loans, re-entrancy, front-running
   - Identify technical anomalies: suspicious signatures, timing patterns
   - Assess risks to other users and the network

3. CONTEXTUAL DECISION:
   - Don't just look at the amount - consider CONTEXT and HISTORY
   - A 1M QUBIC transaction from a known whale might be NORMAL
   - A 10k QUBIC transaction with suspicious patterns might be CRITICAL

Respond in this EXACT JSON format:
{
  "risk_score": <number 0-100 - be precise, justify your score>,
  "risk_level": "<LOW|MEDIUM|HIGH|CRITICAL>",
  "threat_type": "<NORMAL|WHALE_DUMP|WASH_TRADING|FLASH_ATTACK|SPAM|SUSPICIOUS_PATTERN|MARKET_MANIPULATION|SECURITY_THREAT>",
  "explanation": "<intelligent technical explanation - explain YOUR reasoning, not just the result>",
  "factors": ["<detailed factor 1>", "<detailed factor 2>", "<detailed factor 3>"],
  "recommendation": "<Block|Monitor|Ignore|Investigate|Alert>",
  "confidence": <0-100 - your confidence in this analysis>
}

Be intelligent, context-aware, and justify your decisions."""
        
        return prompt
    
    def _parse_ai_response(self, ai_response: str, transaction: Transaction) -> Dict[str, Any]:
        """Parse LLM JSON response"""
        import json
        import re
        
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'\{[\s\S]*\}', ai_response)
            if json_match:
                ai_data = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in response")
            
            # Build risk factors
            risk_factors = []
            if ai_data.get("factors"):
                for factor in ai_data["factors"]:
                    risk_factors.append({
                        "factor": factor,
                        "severity": self._infer_severity(ai_data.get("risk_score", 0)),
                        "details": factor,
                    })
            
            return {
                "risk_score": min(100, max(0, ai_data.get("risk_score", 0))),
                "risk_level": ai_data.get("risk_level", "LOW"),
                "threat_type": ai_data.get("threat_type", "NORMAL"),
                "explanation": ai_data.get("explanation", "Transaction analyzed by AI"),
                "risk_factors": risk_factors,
                "recommendation": ai_data.get("recommendation", "Monitor"),
                "ai_generated": True,
            }
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return self._fallback_analysis(transaction)
    
    def _infer_severity(self, risk_score: float) -> str:
        """Infer severity from risk score"""
        if risk_score >= 70:
            return "high"
        elif risk_score >= 40:
            return "medium"
        else:
            return "low"
    
    def _fallback_analysis(self, transaction: Transaction) -> Dict[str, Any]:
        """Fallback rule-based analysis if LLM unavailable"""
        risk_score = 0
        factors = []
        
        if transaction.amount > 50000:
            risk_score += 30
            factors.append({
                "factor": "Large Amount",
                "severity": "medium",
                "details": f"Large transaction: {transaction.amount:,.2f} QUBIC",
            })
        
        if transaction.source_id == transaction.dest_id:
            risk_score += 70
            factors.append({
                "factor": "Wash Trading",
                "severity": "high",
                "details": "Self-transfer detected",
            })
        
        risk_level = (
            "CRITICAL" if risk_score >= 70
            else "HIGH" if risk_score >= 40
            else "MEDIUM" if risk_score >= 20
            else "LOW"
        )
        
        return {
            "risk_score": min(100, risk_score),
            "risk_level": risk_level,
            "threat_type": "SUSPICIOUS_PATTERN" if risk_score > 20 else "NORMAL",
            "explanation": f"Rule-based analysis: {risk_level} risk detected",
            "risk_factors": factors,
            "recommendation": "Monitor" if risk_score < 50 else "Investigate",
            "ai_generated": False,
        }
    
    def compute_risk_score(
        self,
        transaction: Transaction,
        features: Dict[str, Any],
        wallet_history: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive risk scoring function combining multiple factors
        
        Args:
            transaction: Transaction to score
            features: Extracted features from transaction
            wallet_history: Optional wallet historical data
            
        Returns:
            {
                "risk_score": float (0-100),
                "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
                "factors": List[Dict[str, Any]]  # each factor with name, impact, detail
            }
        """
        risk_score = 0.0
        factors: List[Dict[str, Any]] = []
        
        # 1. Transaction amount relative to baseline
        baseline_amount = getattr(settings, 'RISK_BASELINE_AMOUNT', 10000.0)
        amount_ratio = transaction.amount / baseline_amount if baseline_amount > 0 else 0
        
        if amount_ratio > 10:  # 10x baseline
            amount_impact = min(50, amount_ratio * 2)
            risk_score += amount_impact
            factors.append({
                "factor": "Amount Deviation",
                "impact": amount_impact,
                "detail": f"Transaction amount ({transaction.amount:,.2f} QUBIC) is {amount_ratio:.1f}x baseline",
                "severity": "high" if amount_impact > 30 else "medium"
            })
        elif amount_ratio > 5:  # 5x baseline
            amount_impact = 20
            risk_score += amount_impact
            factors.append({
                "factor": "Amount Deviation",
                "impact": amount_impact,
                "detail": f"Transaction amount ({transaction.amount:,.2f} QUBIC) is {amount_ratio:.1f}x baseline",
                "severity": "medium"
            })
        
        # 2. Recent activity level (tx count in time window)
        wallet_id = transaction.source_id
        window_minutes = getattr(settings, 'RISK_ACTIVITY_WINDOW_MINUTES', 10)
        window_start = datetime.now() - timedelta(minutes=window_minutes)
        
        if wallet_id not in self.wallet_activity:
            self.wallet_activity[wallet_id] = []
        
        # Add current transaction
        self.wallet_activity[wallet_id].append(datetime.now())
        
        # Count transactions in window
        recent_txs = [tx_time for tx_time in self.wallet_activity[wallet_id] if tx_time >= window_start]
        tx_frequency = len(recent_txs)
        
        # Clean old entries (keep only last hour)
        cutoff = datetime.now() - timedelta(hours=1)
        self.wallet_activity[wallet_id] = [tx_time for tx_time in self.wallet_activity[wallet_id] if tx_time >= cutoff]
        
        if tx_frequency > 50:  # Very high frequency
            activity_impact = 40
            risk_score += activity_impact
            factors.append({
                "factor": "High Activity Level",
                "impact": activity_impact,
                "detail": f"{tx_frequency} transactions in last {window_minutes} minutes",
                "severity": "high"
            })
        elif tx_frequency > 20:  # High frequency
            activity_impact = 20
            risk_score += activity_impact
            factors.append({
                "factor": "High Activity Level",
                "impact": activity_impact,
                "detail": f"{tx_frequency} transactions in last {window_minutes} minutes",
                "severity": "medium"
            })
        
        # 3. Transaction type classification
        tx_type_risk = {
            "transfer": 0,
            "wash_trading": 80,
            "flash_loan": 90,
            "contract_call": 15,
            "mixer": 95,
            "spam": 70,
        }
        
        tx_type = transaction.type or "transfer"
        type_risk = tx_type_risk.get(tx_type, 10)
        
        if type_risk > 20:
            risk_score += type_risk
            factors.append({
                "factor": "Transaction Type",
                "impact": type_risk,
                "detail": f"Transaction type '{tx_type}' has elevated risk profile",
                "severity": "high" if type_risk > 50 else "medium"
            })
        
        # 4. Deviation from wallet's historical average (if available)
        if wallet_history:
            historical_avg = wallet_history.get("avg_amount", 0)
            if historical_avg > 0:
                deviation_ratio = abs(transaction.amount - historical_avg) / historical_avg
                
                if deviation_ratio > 5.0:  # 5x deviation
                    deviation_impact = min(30, deviation_ratio * 5)
                    risk_score += deviation_impact
                    factors.append({
                        "factor": "Historical Deviation",
                        "impact": deviation_impact,
                        "detail": f"Amount deviates {deviation_ratio:.1f}x from wallet average ({historical_avg:,.2f} QUBIC)",
                        "severity": "high" if deviation_impact > 20 else "medium"
                    })
        
        # 5. Self-transfer detection
        if transaction.source_id == transaction.dest_id:
            self_transfer_impact = 70
            risk_score += self_transfer_impact
            factors.append({
                "factor": "Self-Transfer",
                "impact": self_transfer_impact,
                "detail": "Transaction source and destination are the same (potential wash trading)",
                "severity": "high"
            })
        
        # Determine risk level
        if risk_score >= 90:
            risk_level = "CRITICAL"
        elif risk_score >= 70:
            risk_level = "HIGH"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "risk_score": min(100.0, max(0.0, risk_score)),
            "risk_level": risk_level,
            "factors": factors
        }
    
    def classify_priority(
        self,
        risk_score: float,
        predicted_risk: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Auto-triage classification for risk events
        
        Args:
            risk_score: Current risk score (0-100)
            predicted_risk: Optional predicted future risk score
            
        Returns:
            {
                "priority": int (1-5, 1 = highest),
                "category": str (WHALE_DUMP, SPAM_ACTIVITY, etc.)
            }
        """
        # Determine priority (1 = highest, 5 = lowest)
        if risk_score >= 90:
            priority = 1
        elif risk_score >= 75:
            priority = 2
        elif risk_score >= 50:
            priority = 3
        elif risk_score >= 25:
            priority = 4
        else:
            priority = 5
        
        # Adjust priority based on predicted risk
        if predicted_risk is not None:
            if predicted_risk > risk_score + 20:  # Significant increase predicted
                priority = max(1, priority - 1)  # Increase priority
            elif predicted_risk < risk_score - 20:  # Significant decrease predicted
                priority = min(5, priority + 1)  # Decrease priority
        
        # Determine category based on score and context
        if risk_score >= 85:
            category = "WHALE_DUMP"
        elif risk_score >= 70:
            category = "SUSPICIOUS_CLUSTER"
        elif risk_score >= 60:
            category = "SPAM_ACTIVITY"
        elif risk_score >= 45:
            category = "ANOMALOUS_PATTERN"
        else:
            category = "NORMAL_ACTIVITY"
        
        return {
            "priority": priority,
            "category": category
        }

