"""
Aegis Brain - LangChain Alternative Implementation
Fallback if Groq direct integration fails
"""
from typing import Dict, Any, Optional
import os
import json
import re

# Try to import LangChain
try:
    from langchain_groq import ChatGroq
    from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("WARNING: langchain-groq not available. Install with: pip install langchain-groq")


class AegisBrainLangChain:
    """
    LangChain-based AI brain for QUBIC AEGIS
    Alternative implementation using LangChain for better reliability
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI brain with LangChain
        
        Args:
            api_key: Groq API key (or from env GROQ_API_KEY)
        """
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        if not LANGCHAIN_AVAILABLE:
            print("WARNING: langchain-groq not available. AegisBrainLangChain will use fallback analysis.")
            self.llm = None
            return
            
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            print("WARNING: GROQ_API_KEY not set. AegisBrainLangChain will use fallback analysis.")
            self.llm = None
        else:
            try:
                # Initialize LangChain Groq client
                self.llm = ChatGroq(
                    groq_api_key=self.api_key,
                    model_name=self.model,
                    temperature=0.5,
                    max_tokens=1000
                )
                print("✅ AegisBrainLangChain initialized with LangChain + Groq")
            except Exception as e:
                print(f"WARNING: Could not initialize LangChain Groq client: {e}")
                self.llm = None
    
    async def analyze_transaction(self, tx_data: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Deep AI analysis using LangChain
        
        Args:
            tx_data: Transaction data dictionary
            context: Optional context (wallet history, network state, etc.)
            
        Returns:
            Complete AI analysis with risk score, anomaly type, and recommendations
        """
        if not self.llm:
            return self._fallback_analysis(tx_data)
        
        # Build prompt template
        system_template = """You are AEGIS, a military-grade AI cybersecurity system for the Qubic Blockchain with deep expertise in:
- Blockchain attack detection (flash loans, re-entrancy, front-running)
- Fraud analysis and market manipulation (wash trading, pump & dump)
- Behavioral analysis of wallets and suspicious patterns
- Security threat intelligence for blockchains

You analyze each transaction with a multi-dimensional approach:
- Agent Scanner: Examines raw data and technical metrics
- Agent Profiler: Analyzes history, behavioral patterns and deviations
- Agent Commander: Makes the final decision based on comprehensive analysis

Be intelligent, contextual, and justify your decisions. Respond ONLY with valid JSON, no markdown, no code blocks."""

        human_template = """You are AEGIS, an expert AI in Qubic blockchain cybersecurity with years of experience in attack and fraud detection.

TASK: Analyze this transaction and determine the REAL risk level using your expertise, not just simple rules.

TRANSACTION DATA:
- Source: {source_id}
- Destination: {dest_id}
- Amount: {amount:,.2f} QUBIC
- Type: {type}
- Tick: {tick}
- Token: {token_symbol} ({token_name})
- Timestamp: {timestamp}

{context}

ANALYSIS INSTRUCTIONS (be intelligent, not just rule-based):

1. BEHAVIORAL ANALYSIS:
   - Compare this amount with wallet history (if available)
   - Detect suspicious patterns (self-transfers, rapid sequences, abnormal amounts)
   - Identify manipulation attempts (wash trading, pump & dump, etc.)

2. SECURITY ANALYSIS:
   - Detect potential attacks (flash loans, re-entrancy patterns)
   - Identify technical anomalies (suspicious signatures, abnormal timings)
   - Assess risks to other users

3. TOKEN CONTEXT:
   - If a token is involved, consider token-specific risks
   - Assess impact on token liquidity and stability

4. INTELLIGENT DECISION:
   - Do NOT base decision solely on amount
   - Consider CONTEXT and HISTORY
   - Use your expertise to detect subtle patterns

REQUIRED - Respond with this EXACT JSON (be precise and justify):

{{
  "risk_score": <number 0-100 - be precise, not arbitrary>,
  "risk_level": "<LOW|MEDIUM|HIGH|CRITICAL>",
  "analysis": "<precise technical phrase in English, max 150 chars, explain YOUR decision>",
  "anomaly_type": "<None|Whale|WashTrading|FlashLoan|Spam|SuspiciousPattern|MarketManipulation|SecurityThreat>",
  "recommendation": "<Block|Monitor|Ignore|Investigate|Alert>",
  "factors": ["<detailed factor 1>", "<detailed factor 2>", "<detailed factor 3>"],
  "confidence": <number 0-100 - your confidence in this analysis>,
  "threat_description": "<detailed technical description of threat if detected, otherwise empty>"
}}

IMPORTANT: Be intelligent and contextual. A 1M QUBIC transaction from a known whale might be normal, while a 10k QUBIC transaction with suspicious patterns might be critical."""

        # Build context string
        context_str = ""
        if context:
            context_str = "\nENRICHED CONTEXT (use this for your analysis):\n"
            if context.get('wallet_tx_count'):
                context_str += f"- Wallet history: {context['wallet_tx_count']} previous transactions\n"
            if context.get('wallet_avg_amount'):
                context_str += f"- Historical average amount: {context['wallet_avg_amount']:,.2f} QUBIC\n"
                current_amount = tx_data.get('amount', 0)
                avg_amount = context.get('wallet_avg_amount', 1)
                if avg_amount > 0:
                    deviation = abs(current_amount - avg_amount) / avg_amount * 100
                    context_str += f"- DEVIATION vs history: {deviation:.1f}% {'(ABNORMAL)' if deviation > 100 else '(normal)'}\n"
            if context.get('wallet_total_volume'):
                context_str += f"- Total wallet volume: {context['wallet_total_volume']:,.2f} QUBIC\n"
            if context.get('is_whale'):
                context_str += "- ⚠️ WHALE WALLET DETECTED - Potential market manipulation pattern\n"
        
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
        
        try:
            # Format prompt
            formatted_prompt = prompt.format_messages(
                source_id=tx_data.get('source_id', 'Unknown')[:30] + "...",
                dest_id=tx_data.get('dest_id', 'Unknown')[:30] + "...",
                amount=tx_data.get('amount', 0),
                type=tx_data.get('type', 'transfer'),
                tick=tx_data.get('tick', 0),
                token_symbol=tx_data.get('token_symbol', 'N/A'),
                token_name=tx_data.get('token_name', 'N/A'),
                timestamp=tx_data.get('timestamp', 'N/A'),
                context=context_str
            )
            
            # Call LLM
            response = self.llm.invoke(formatted_prompt)
            ai_response = response.content
            
            return self._parse_ai_response(ai_response, tx_data)
            
        except Exception as e:
            print(f"Error in LangChain AI Brain analysis: {e}")
            return self._fallback_analysis(tx_data)
    
    def _parse_ai_response(self, ai_response: str, tx_data: Dict) -> Dict[str, Any]:
        """Parse AI JSON response"""
        try:
            # Clean response (remove markdown if present)
            cleaned = re.sub(r'```json\n?|\n?```', '', ai_response).strip()
            cleaned = re.sub(r'^[^{]*', '', cleaned)  # Remove text before JSON
            cleaned = re.sub(r'[^}]*$', '', cleaned)  # Remove text after JSON
            cleaned = cleaned + '}'
            
            ai_data = json.loads(cleaned)
            
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
                "risk_score": min(100, max(0, float(ai_data.get("risk_score", 0)))),
                "risk_level": ai_data.get("risk_level", "LOW"),
                "analysis": ai_data.get("analysis", "Transaction analyzed"),
                "anomaly_type": ai_data.get("anomaly_type", "None"),
                "recommendation": ai_data.get("recommendation", "Monitor"),
                "risk_factors": risk_factors,
                "confidence": min(100, max(0, float(ai_data.get("confidence", 80)))),
                "threat_description": ai_data.get("threat_description", ""),
                "ai_generated": True,
            }
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            print(f"Raw response: {ai_response[:200]}")
            return self._fallback_analysis(tx_data)
    
    def _infer_severity(self, risk_score: float) -> str:
        """Infer severity from risk score"""
        if risk_score >= 70:
            return "high"
        elif risk_score >= 40:
            return "medium"
        else:
            return "low"
    
    def _fallback_analysis(self, tx_data: Dict) -> Dict[str, Any]:
        """Fallback analysis if AI fails"""
        risk_score = 0
        factors = []
        
        if tx_data.get("amount", 0) > 50000:
            risk_score += 30
            factors.append("Large transaction amount")
        
        if tx_data.get("source_id") == tx_data.get("dest_id"):
            risk_score += 70
            factors.append("Self-transfer detected")
        
        risk_level = (
            "CRITICAL" if risk_score >= 70
            else "HIGH" if risk_score >= 40
            else "MEDIUM" if risk_score >= 20
            else "LOW"
        )
        
        return {
            "risk_score": min(100, risk_score),
            "risk_level": risk_level,
            "analysis": f"Rule-based analysis: {risk_level} risk",
            "anomaly_type": "SuspiciousPattern" if risk_score > 20 else "None",
            "recommendation": "Monitor" if risk_score < 50 else "Investigate",
            "risk_factors": [{"factor": f, "severity": "medium", "details": f} for f in factors],
            "confidence": 60,
            "threat_description": "",
            "ai_generated": False,
        }

