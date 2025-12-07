"""
Agent Automator (V2 - Expert Edition)
Capabilities:
- Automated Response Decision Logic (AI-driven)
- Integration with n8n / EasyConnect
- Smart Contract Interaction (Mocked for safety)
- Payload Formatting for Rich Discord Embeds
"""
import os
import json
import aiohttp
from typing import Dict, Any
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class AgentAutomator:
    """
    The 'Hands' of Aegis.
    Executes defensive actions based on the intelligence provided by other agents.
    """
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = os.getenv("GROQ_MODEL")
        self.n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL")

    async def decide_and_execute(self, risk_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        1. AI decides the best response protocol.
        2. Executes the action (e.g., calls n8n).
        """
        
        # 1. AI Decision Making
        prompt = f"""
        You are the Automated Defense System for Qubic.
        EVENT: {risk_event.get('attack_type')}
        SEVERITY: {risk_event.get('risk_level')} (Score: {risk_event.get('risk_score')})
        DETAILS: {risk_event.get('reasoning')}
        
        Available Protocols:
        - "LOG_ONLY": Low risk events.
        - "NOTIFY_COMMUNITY": Medium risk (Discord Alert).
        - "NOTIFY_ADMIN_URGENT": High risk (SMS/Call via EasyConnect).
        - "TRIGGER_CIRCUIT_BREAKER": Critical risk (Call Smart Contract to pause trading).
        
        Task: Choose the single best protocol and write a short action message.
        Return JSON: {{"protocol": "...", "message": "..."}}
        """
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            decision = json.loads(completion.choices[0].message.content)
            
            # 2. Execution Logic
            execution_result = {"status": "skipped", "details": "No action required"}
            
            if decision["protocol"] != "LOG_ONLY":
                # Prepare payload for n8n (EasyConnect)
                payload = self._construct_n8n_payload(risk_event, decision)
                
                # Send Webhook (Fire and Forget)
                if self.n8n_webhook_url:
                    await self._send_webhook(payload)
                    execution_result = {"status": "sent", "target": "n8n/EasyConnect"}
                else:
                    execution_result = {"status": "failed", "details": "No Webhook URL configured"}
            
            return {
                "decision": decision,
                "execution": execution_result
            }

        except Exception as e:
            print(f"Automator Error: {e}")
            return {"error": str(e)}

    def _construct_n8n_payload(self, risk, decision) -> Dict[str, Any]:
        """
        Constructs the exact JSON structure expected by our n8n workflow
        to generate the beautiful Red Card on Discord.
        """
        return {
            "risk_score": risk.get('risk_score', 0),
            "type": risk.get('attack_type', 'UNKNOWN'),
            "analysis": decision.get('message') + "\n\n" + risk.get('reasoning', ''),
            "severity": risk.get('risk_level', 'MEDIUM'),
            "protocol": decision.get('protocol')
        }

    async def _send_webhook(self, payload: Dict[str, Any]):
        """Async HTTP POST to n8n"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.n8n_webhook_url, json=payload) as resp:
                    print(f"Webhook sent! Status: {resp.status}")
            except Exception as e:
                print(f" Webhook failed: {e}")