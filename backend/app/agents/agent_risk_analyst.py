"""
Agent Risk Analyst (V2 - Expert Edition)
Capabilities:
- Deep Semantic Analysis via LangChain + Groq
- Contextual Threat Modeling (Nostromo/QubicTrade specific)
- Structured JSON Output for Frontend
- Explainable AI (XAI) generation
"""
import os
import json
from typing import Dict, Any, List
from dotenv import load_dotenv

# LangChain Imports (Optional - with fallback)
try:
    from langchain_groq import ChatGroq
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ LangChain not available: {e}. Risk Analyst will use fallback mode.")
    LANGCHAIN_AVAILABLE = False
    ChatGroq = None
    ChatPromptTemplate = None
    JsonOutputParser = None

from pydantic import BaseModel, Field

from app.config import settings

load_dotenv()

# Define the expected output structure (Strict JSON)
class RiskAnalysisOutput(BaseModel):
    risk_score: int = Field(description="Score between 0 and 100 representing the threat level")
    risk_level: str = Field(description="Severity classification: LOW, MEDIUM, HIGH, or CRITICAL")
    attack_type: str = Field(description="Type of threat (e.g., WHALE_DUMP, RUG_PULL, WASH_TRADING, NONE)")
    reasoning: str = Field(description="Short, technical explanation for the security dashboard")
    action_recommendation: str = Field(description="Recommended action (e.g., MONITOR, FREEZE, ALERT, BLOCK)")

class AgentRiskAnalyst:
    """
    The 'Brain' of Aegis.
    Uses LLM reasoning to determine if a pattern is malicious based on context.
    """
    
    def __init__(self):
        self.langchain_available = LANGCHAIN_AVAILABLE
        
        if not self.langchain_available:
            print("⚠️ Risk Analyst: LangChain not available, using fallback mode")
            self.llm = None
            self.chain = None
            return
            
        # Initialize Groq LLM via LangChain (Llama-3-70b for maximum intelligence)
        # We use temperature 0.1 for factual, consistent, non-hallucinated responses.
        model_name = settings.GROQ_MODEL
        groq_api_key = settings.GROQ_API_KEY
        
        if not model_name:
            raise ValueError("GROQ_MODEL environment variable is not set. Default: llama-3.3-70b-versatile")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
            
        try:
            self.llm = ChatGroq(
                temperature=0.1, 
                model_name=model_name,
                groq_api_key=groq_api_key
            )
            
            self.parser = JsonOutputParser(pydantic_object=RiskAnalysisOutput)
            
            # The Expert System Prompt
            self.prompt = ChatPromptTemplate.from_messages([
                ("system", """
                You are QUBIC AEGIS, a Senior Blockchain Security Auditor specializing in the Qubic Network.
                Your job is to analyze transaction metadata and detect sophisticated financial threats.
                
                DOMAIN CONTEXT:
                - "Nostromo": A Qubic launchpad where Rug Pulls (devs dumping tokens) are the main threat.
                - "QubicTrade": A DEX where Whale Dumps, Front-running, and Wash Trading occur.
                - "Dusting": Tiny transactions used to de-anonymize wallets.
                
                ANALYSIS RULES:
                1. Be paranoid. High volumes from unknown wallets are highly suspicious.
                2. Rapid frequency (Bot behavior) combined with selling is a CRITICAL risk.
                3. Always provide 'reasoning' that sounds professional (Cybersecurity & DeFi jargon).
                4. If the risk score is above 80, the level must be HIGH or CRITICAL.
                
                You must respond in valid JSON format only, matching the requested schema.
                """),
                ("human", """
                Analyze this transaction context:
                {transaction_context}
                
                Format instructions: {format_instructions}
                """)
            ])
            
            self.chain = self.prompt | self.llm | self.parser
        except Exception as e:
            print(f"⚠️ Failed to initialize LangChain Groq: {e}. Using fallback mode.")
            self.langchain_available = False
            self.llm = None
            self.chain = None

    async def analyze(self, enriched_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis function.
        Takes data from AgentCollector -> Returns Risk Assessment.
        """
        # Optimization: If the Collector tagged it as noise, skip expensive LLM call
        if enriched_data.get("ai_tag") == "NOISE":
            return {
                "risk_score": 5,
                "risk_level": "LOW",
                "attack_type": "DUST_NOISE",
                "reasoning": "Transaction identified as low-value dust/noise by collector heuristics.",
                "action_recommendation": "IGNORE"
            }

        # Build context for the AI
        context_str = f"""
        - Source Wallet: {enriched_data.get('source_id')}
        - Dest Wallet: {enriched_data.get('dest_id')}
        - Amount: {enriched_data.get('amount')} {enriched_data.get('token', 'QUBIC')}
        - Bot Probability: {enriched_data.get('is_bot_probable')}
        - Dusting Attempt: {enriched_data.get('is_dusting_attempt')}
        - Collector Tag: {enriched_data.get('ai_tag')}
        """

        # If LangChain not available, use fallback
        if not self.langchain_available or not self.chain:
            return self._fallback_analysis(enriched_data)
        
        try:
            # Invoke Groq via LangChain
            result = self.chain.invoke({
                "transaction_context": context_str,
                "format_instructions": self.parser.get_format_instructions()
            })
            return result
            
        except Exception as e:
            print(f"AI Analysis Failed: {e}")
            # Fallback mechanism in case of API failure
            return self._fallback_analysis(enriched_data)
    
    def _fallback_analysis(self, enriched_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when LangChain is not available"""
        # Simple heuristic-based analysis
        amount = enriched_data.get('amount', 0)
        is_bot = enriched_data.get('is_bot_probable', False)
        is_dusting = enriched_data.get('is_dusting_attempt', False)
        
        if is_dusting:
            return {
                "risk_score": 15,
                "risk_level": "LOW",
                "attack_type": "DUST_NOISE",
                "reasoning": "Dusting attempt detected. Low risk but flagged for monitoring.",
                "action_recommendation": "MONITOR"
            }
        
        if amount > 500000 and is_bot:
            return {
                "risk_score": 85,
                "risk_level": "HIGH",
                "attack_type": "WHALE_DUMP",
                "reasoning": "Large transaction from bot-like wallet detected. Possible whale dump.",
                "action_recommendation": "ALERT"
            }
        
        if amount > 500000:
            return {
                "risk_score": 70,
                "risk_level": "MEDIUM",
                "attack_type": "LARGE_TRANSFER",
                "reasoning": "Large transaction detected. Monitoring for suspicious patterns.",
                "action_recommendation": "MONITOR"
            }
        
        return {
            "risk_score": 20,
            "risk_level": "LOW",
            "attack_type": "NORMAL",
            "reasoning": "Transaction appears normal. No immediate threats detected.",
            "action_recommendation": "MONITOR"
        }