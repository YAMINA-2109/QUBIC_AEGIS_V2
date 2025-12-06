"""
Aegis Brain - Core AI Intelligence Engine
Uses Groq for real-time, intelligent transaction analysis
"""
from typing import Dict, Any, Optional
import os
import json
import re
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
# Try multiple locations: backend/.env, root/.env, current directory
_env_locations = [
    Path(__file__).parent.parent.parent / '.env',  # backend/.env
    Path(__file__).parent.parent.parent.parent / '.env',  # root/.env (qubic-aegis/.env)
    Path.cwd() / '.env',  # current directory
    Path.cwd().parent / '.env',  # parent directory
]

_env_loaded = False
for env_loc in _env_locations:
    if env_loc.exists():
        load_dotenv(dotenv_path=env_loc, override=True)
        _env_loaded = True
        print(f"✅ Loaded .env from: {env_loc}")
        break

if not _env_loaded:
    # Last resort: try default location
    load_dotenv(override=True)

from app.models.transaction import Transaction

# Import Groq with error handling for version compatibility
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("WARNING: groq package not available. AI features will be disabled.")


class AegisBrain:
    """
    Core AI brain for QUBIC AEGIS
    Orchestrates multi-agent AI analysis using Groq
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI brain
        
        Args:
            api_key: Groq API key (or from env GROQ_API_KEY)
        """
        # Reload .env to ensure we have the latest values (multiple locations)
        for env_loc in _env_locations:
            if env_loc.exists():
                load_dotenv(dotenv_path=env_loc, override=True)
                break
        else:
            load_dotenv(override=True)
        
        # Use more powerful model for stronger AI analysis
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")  # Default: Fast and intelligent
        # Available models: llama-3.3-70b-versatile, llama-3.1-70b-versatile, mixtral-8x7b-32768
        
        if not GROQ_AVAILABLE:
            print("WARNING: groq package not available. AegisBrain will use fallback analysis.")
            self.client = None
            return
            
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            print("WARNING: GROQ_API_KEY not found in environment variables.")
            print(f"DEBUG: Checked .env locations: {[str(loc) for loc in _env_locations]}")
            print(f"DEBUG: Current working directory: {os.getcwd()}")
            print("AegisBrain will use fallback analysis (no AI).")
            self.client = None
        else:
            try:
                # Initialize Groq client
                self.client = Groq(api_key=self.api_key)
                # Test the connection with a simple call
                try:
                    _ = self.client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": "test"}],
                        max_tokens=5
                    )
                    print(f"AegisBrain initialized with Groq (model: {self.model})")
                except Exception as test_error:
                    print(f"WARNING: Groq API test failed: {test_error}")
                    print("AI Brain will use fallback responses. Please check GROQ_API_KEY and network connection.")
                    print("TIP: Try installing langchain-groq as alternative: pip install langchain-groq")
                    self.client = None
            except (TypeError, AttributeError) as e:
                # Handle version compatibility issues (e.g., proxies parameter)
                print(f"WARNING: Groq initialization error (possible version issue): {e}")
                print("AI Brain will use fallback responses. Please check groq package version.")
                print("TIP: Try installing langchain-groq as alternative: pip install langchain-groq")
                self.client = None
            except Exception as e:
                print(f"WARNING: Could not initialize Groq client: {e}")
                print("AI Brain will use fallback responses. Please check GROQ_API_KEY and network connection.")
                print("TIP: Try installing langchain-groq as alternative: pip install langchain-groq")
                self.client = None
    
    async def analyze_transaction(self, tx_data: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Deep AI analysis of a transaction using multi-agent reasoning
        
        Args:
            tx_data: Transaction data dictionary
            context: Optional context (wallet history, network state, etc.)
            
        Returns:
            Complete AI analysis with risk score, anomaly type, and recommendations
        """
        if not self.client:
            return self._fallback_analysis(tx_data)
        
        # Build comprehensive prompt
        prompt = self._build_analysis_prompt(tx_data, context)
        
        try:
            # Call Groq with specialized system prompt
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are AEGIS, a military-grade AI cybersecurity system for the Qubic Blockchain with deep expertise in:
- Blockchain attack detection (flash loans, re-entrancy, front-running)
- Fraud analysis and market manipulation (wash trading, pump & dump)
- Behavioral analysis of wallets and suspicious patterns
- Security threat intelligence for blockchains

You analyze each transaction with a multi-dimensional approach:
- Agent Scanner: Examines raw data and technical metrics
- Agent Profiler: Analyzes history, behavioral patterns and deviations
- Agent Commander: Makes the final decision based on comprehensive analysis

Be intelligent, contextual, and justify your decisions. Respond ONLY with valid JSON, no markdown, no code blocks."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,  # More precise for security analysis
                max_tokens=1000,  # More tokens for detailed analysis
                response_format={"type": "json_object"} if self._supports_json_mode() else None,
            )
            
            ai_response = response.choices[0].message.content
            return self._parse_ai_response(ai_response, tx_data)
            
        except Exception as e:
            print(f"Error in AI Brain analysis: {e}")
            return self._fallback_analysis(tx_data)
    
    def _build_analysis_prompt(self, tx_data: Dict, context: Optional[Dict]) -> str:
        """Build comprehensive analysis prompt with enhanced context for stronger AI reasoning"""
        prompt = f"""You are AEGIS, an expert AI in Qubic blockchain cybersecurity with years of experience in attack and fraud detection.

TASK: Analyze this transaction and determine the REAL risk level using your expertise, not just simple rules.

TRANSACTION DATA:
- Source: {tx_data.get('source_id', 'Unknown')[:30]}...
- Destination: {tx_data.get('dest_id', 'Unknown')[:30]}...
- Amount: {tx_data.get('amount', 0):,.2f} QUBIC
- Type: {tx_data.get('type', 'transfer')}
- Tick: {tx_data.get('tick', 0)}
- Token: {tx_data.get('token_symbol', 'N/A')} ({tx_data.get('token_name', 'N/A')})
- Timestamp: {tx_data.get('timestamp', 'N/A')}
"""
        
        if context:
            prompt += f"\nENRICHED CONTEXT (use this for your analysis):\n"
            if context.get('wallet_tx_count'):
                prompt += f"- Wallet history: {context['wallet_tx_count']} previous transactions\n"
            if context.get('wallet_avg_amount'):
                prompt += f"- Historical average amount: {context['wallet_avg_amount']:,.2f} QUBIC\n"
                current_amount = tx_data.get('amount', 0)
                avg_amount = context.get('wallet_avg_amount', 1)
                if avg_amount > 0:
                    deviation = abs(current_amount - avg_amount) / avg_amount * 100
                    prompt += f"- DEVIATION vs history: {deviation:.1f}% {'(ABNORMAL)' if deviation > 100 else '(normal)'}\n"
            if context.get('wallet_total_volume'):
                prompt += f"- Total wallet volume: {context['wallet_total_volume']:,.2f} QUBIC\n"
            if context.get('is_whale'):
                prompt += "- ⚠️ WHALE WALLET DETECTED - Potential market manipulation pattern\n"
            if context.get('features'):
                features = context.get('features', {})
                prompt += f"- Technical features: amount_log={features.get('amount_log', 0):.2f}, is_self_transfer={features.get('is_self_transfer', False)}\n"
        
        prompt += """
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

{
  "risk_score": <number 0-100 - be precise, not arbitrary>,
  "risk_level": "<LOW|MEDIUM|HIGH|CRITICAL>",
  "analysis": "<precise technical phrase in English, max 150 chars, explain YOUR decision>",
  "anomaly_type": "<None|Whale|WashTrading|FlashLoan|Spam|SuspiciousPattern|MarketManipulation|SecurityThreat>",
  "recommendation": "<Block|Monitor|Ignore|Investigate|Alert>",
  "factors": ["<detailed factor 1>", "<detailed factor 2>", "<detailed factor 3>"],
  "confidence": <number 0-100 - your confidence in this analysis>,
  "threat_description": "<detailed technical description of threat if detected, otherwise empty>"
}

IMPORTANT: Be intelligent and contextual. A 1M QUBIC transaction from a known whale might be normal, while a 10k QUBIC transaction with suspicious patterns might be critical."""
        
        return prompt
    
    def _supports_json_mode(self) -> bool:
        """Check if model supports JSON mode"""
        return "llama-3.3" in self.model or "llama-3" in self.model
    
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
    
    async def chat(self, question: str, context: Optional[Dict] = None) -> str:
        """
        Chat with Aegis AI - Answer questions about security, risks, etc.
        
        Args:
            question: User question
            context: Optional context (recent transactions, alerts, etc.)
            
        Returns:
            AI response as text
        """
        if not self.client:
            return "I'm AEGIS, your AI security copilot. Groq API is not configured. Please set GROQ_API_KEY in .env file for full AI capabilities."
        
        prompt = f"""You are AEGIS, an expert AI in Qubic blockchain cybersecurity.

User question: {question}
"""
        
        if context:
            prompt += f"\nContext:\n- Recent transactions analyzed: {context.get('recent_txs', 0)}\n"
            prompt += f"- Current risk score: {context.get('current_risk', 0)}\n"
        
        prompt += "\nRespond in a technical but accessible manner, in English. Be concise and precise."
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are AEGIS, an expert AI cybersecurity analyst for Qubic blockchain with deep knowledge in:
- Blockchain security threats and attack vectors
- Market manipulation patterns and fraud detection
- Risk assessment and threat intelligence
- Qubic ecosystem specifics and token mechanics

Provide intelligent, technical, accurate, and context-aware answers. Use your expertise to give insights, not just repeat information."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.6,  # Slightly creative but precise
                max_tokens=600,
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    async def explain_risk_decision(
        self,
        features: Dict[str, Any],
        risk_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate systematic Explainable AI explanation for risk decisions
        
        Args:
            features: Transaction features extracted
            risk_analysis: Risk analysis results
            
        Returns:
            {
                "xai_summary": str,
                "factors": List[Dict[str, Any]]
            }
        """
        if not self.client:
            # Fallback explanation
            return {
                "xai_summary": f"Risk level: {risk_analysis.get('risk_level', 'UNKNOWN')} (Score: {risk_analysis.get('risk_score', 0):.1f}/100)",
                "factors": [
                    {
                        "name": factor.get("factor", "Unknown"),
                        "impact": factor.get("impact", 0),
                        "explanation": factor.get("detail", factor.get("details", ""))
                    }
                    for factor in risk_analysis.get("risk_factors", [])
                ]
            }
        
        # Build prompt for XAI explanation with enhanced intelligence
        prompt = f"""You are AEGIS, an expert AI in Qubic blockchain cybersecurity.

EXPLAIN INTELLIGENTLY this risk decision (use your expertise, not just rules):

Transaction data:
- Amount: {features.get('amount', 0):,.2f} QUBIC
- Type: {risk_analysis.get('threat_type', 'NORMAL')}
- Risk score: {risk_analysis.get('risk_score', 0)}/100
- Level: {risk_analysis.get('risk_level', 'LOW')}

Detected factors:
{chr(10).join('- ' + str(factor.get('factor', 'Unknown')) for factor in risk_analysis.get('risk_factors', [])[:5])}

INSTRUCTIONS:
1. Summarize INTELLIGENTLY why this risk level was assigned
2. Identify CRITICAL factors (not all, just the most important ones)
3. Explain the POTENTIAL impact of this threat
4. Be contextual and precise

Respond in JSON format:
{{
    "summary": "<intelligent and contextual summary in one sentence, explain the REASON, not just the result>",
    "factors": [
        {{
            "name": "<name of critical factor>",
            "impact": <0-100 - importance of this factor>,
            "explanation": "<detailed explanation of why this factor is significant and its impact>"
        }}
    ]
}}

Be intelligent: explain the "WHY" and "HOW", not just the "WHAT"."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are AEGIS, an expert AI security analyst with deep expertise in blockchain cybersecurity, fraud detection, and threat intelligence. 

Your explanations are:
- INTELLIGENT: You understand context and patterns, not just rules
- TECHNICAL: You explain the WHY and HOW, not just the WHAT
- PRECISE: You identify the most critical factors, not everything
- ACTIONABLE: Your explanations help understand and mitigate threats

Always respond with valid JSON."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=400,
                response_format={"type": "json_object"} if self._supports_json_mode() else None,
            )
            
            ai_response = response.choices[0].message.content
            # Parse JSON response
            import json
            import re
            json_match = re.search(r'\{[\s\S]*\}', ai_response)
            if json_match:
                parsed = json.loads(json_match.group())
                return {
                    "xai_summary": parsed.get("summary", ""),
                    "factors": parsed.get("factors", [])
                }
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            print(f"Error generating XAI explanation: {e}")
            # Fallback
            return {
                "xai_summary": f"Risk assessment: {risk_analysis.get('risk_level', 'UNKNOWN')} risk (Score: {risk_analysis.get('risk_score', 0):.1f}/100)",
                "factors": [
                    {
                        "name": factor.get("factor", "Unknown"),
                        "impact": factor.get("impact", 0),
                        "explanation": factor.get("detail", factor.get("details", ""))
                    }
                    for factor in risk_analysis.get("risk_factors", [])[:5]
                ]
            }

