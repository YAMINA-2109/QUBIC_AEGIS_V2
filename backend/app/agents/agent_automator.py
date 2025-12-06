"""
Agent Automator - EasyConnect/n8n Integration Agent
Generates and manages automation workflows
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import requests
from app.models.events import RiskEvent


class AgentAutomator:
    """
    Generates automation workflows for EasyConnect/n8n
    Manages webhook triggers and automation templates
    """
    
    def __init__(self, default_webhook_url: Optional[str] = None):
        """
        Initialize the automator
        
        Args:
            default_webhook_url: Default n8n webhook URL
        """
        self.default_webhook_url = default_webhook_url
        self.workflow_templates = {
            "critical_alert": self._critical_alert_template,
            "whale_detected": self._whale_detected_template,
            "daily_report": self._daily_report_template,
            "risk_threshold": self._risk_threshold_template,
        }
    
    def generate_workflow(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an n8n workflow configuration
        
        Args:
            event_type: Type of event (critical_alert, whale_detected, etc.)
            event_data: Event data to include in workflow (can be RiskEvent dict or regular dict)
            
        Returns:
            Workflow configuration dictionary
        """
        if event_type not in self.workflow_templates:
            return {
                "error": f"Unknown event type: {event_type}",
                "available_types": list(self.workflow_templates.keys()),
            }
        
        template_func = self.workflow_templates[event_type]
        return template_func(event_data)
    
    def process_risk_event(self, risk_event: RiskEvent) -> Dict[str, Any]:
        """
        Process a RiskEvent and generate appropriate automation workflow
        V2 BONUS: Adds Active Defense (simulated firewall block) for CRITICAL risks
        
        Args:
            risk_event: RiskEvent instance
            
        Returns:
            Workflow configuration and trigger payload with active defense
        """
        # Determine event type based on risk level and category
        if risk_event.risk_level == "CRITICAL":
            event_type = "critical_alert"
        elif risk_event.category == "WHALE_DUMP":
            event_type = "whale_detected"
        elif risk_event.risk_score > 70:
            event_type = "risk_threshold"
        else:
            event_type = "critical_alert"  # Default
        
        # Convert RiskEvent to dict for workflow generation
        event_data = risk_event.dict()
        
        # V2 BONUS: Active Defense - Simulate firewall block for CRITICAL risks
        active_defense_action = None
        if risk_event.risk_level == "CRITICAL":
            active_defense_action = self._simulate_active_defense(risk_event)
        
        # Generate workflow
        workflow = self.generate_workflow(event_type, event_data)
        
        # Prepare webhook payload
        payload = {
            "event_id": risk_event.event_id,
            "wallet_id": risk_event.wallet_id,
            "risk_score": risk_event.risk_score,
            "risk_level": risk_event.risk_level,
            "category": risk_event.category,
            "xai_summary": risk_event.xai_summary,
            "timestamp": risk_event.timestamp.isoformat(),
            "recommendation": risk_event.recommendation,
        }
        
        # V2 BONUS: Include active defense in payload body for n8n
        body_payload = {"body": payload}
        if active_defense_action:
            body_payload["body"]["active_defense"] = active_defense_action
        
        return {
            "workflow": workflow,
            "payload": body_payload,  # Wrapped for n8n compatibility
            "body": body_payload["body"],  # Direct access
            "active_defense": active_defense_action,  # V2 BONUS
            "event_type": event_type
        }
    
    def trigger_automation(self, webhook_url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trigger an automation via webhook
        
        Args:
            webhook_url: n8n webhook URL
            payload: Payload to send
            
        Returns:
            Response dictionary
        """
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            
            return {
                "success": True,
                "status_code": response.status_code,
                "message": "Automation triggered successfully",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to trigger automation",
            }
    
    def _critical_alert_template(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate critical alert workflow template"""
        return {
            "name": "QUBIC AEGIS - Critical Alert",
            "nodes": [
                {
                    "name": "Webhook Trigger",
                    "type": "n8n-nodes-base.webhook",
                    "parameters": {
                        "path": "aegis-critical",
                        "httpMethod": "POST",
                    },
                },
                {
                    "name": "Discord Alert",
                    "type": "n8n-nodes-base.discord",
                    "parameters": {
                        "operation": "postMessage",
                        "channel": "{{ $json.channel || 'alerts' }}",
                        "text": "🚨 **CRITICAL ALERT** 🚨\n{{ $json.message }}",
                    },
                },
                {
                    "name": "Telegram Alert",
                    "type": "n8n-nodes-base.telegram",
                    "parameters": {
                        "operation": "sendMessage",
                        "chatId": "{{ $json.telegram_chat_id }}",
                        "text": "🚨 CRITICAL: {{ $json.message }}",
                    },
                },
            ],
            "connections": {
                "Webhook Trigger": {
                    "main": [[{"node": "Discord Alert"}, {"node": "Telegram Alert"}]],
                },
            },
        }
    
    def _whale_detected_template(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate whale detected workflow template"""
        return {
            "name": "QUBIC AEGIS - Whale Detected",
            "nodes": [
                {
                    "name": "Webhook Trigger",
                    "type": "n8n-nodes-base.webhook",
                    "parameters": {"path": "aegis-whale"},
                },
                {
                    "name": "Format Message",
                    "type": "n8n-nodes-base.function",
                    "parameters": {
                        "functionCode": """
                        const data = items[0].json;
                        return [{
                            json: {
                                message: `🐋 Whale Alert: Wallet ${data.wallet_id.substring(0, 10)}... has moved ${data.amount} QUBIC`,
                                risk_score: data.risk_score,
                                timestamp: new Date().toISOString()
                            }
                        }];
                        """,
                    },
                },
                {
                    "name": "Multiple Channels",
                    "type": "n8n-nodes-base.splitInBatches",
                    "parameters": {"batchSize": 1},
                },
            ],
        }
    
    def _daily_report_template(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate daily report workflow template"""
        return {
            "name": "QUBIC AEGIS - Daily Report",
            "nodes": [
                {
                    "name": "Schedule Trigger",
                    "type": "n8n-nodes-base.scheduleTrigger",
                    "parameters": {"rule": {"interval": [{"field": "hours", "hoursInterval": 24}]}},
                },
                {
                    "name": "Generate Report",
                    "type": "n8n-nodes-base.httpRequest",
                    "parameters": {
                        "url": "http://localhost:8000/api/reports/daily",
                        "method": "GET",
                    },
                },
                {
                    "name": "Send Email",
                    "type": "n8n-nodes-base.emailSend",
                    "parameters": {
                        "to": "{{ $json.recipient }}",
                        "subject": "QUBIC AEGIS Daily Security Report",
                        "text": "{{ $json.report }}",
                    },
                },
            ],
        }
    
    def _risk_threshold_template(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate risk threshold workflow template"""
        return {
            "name": "QUBIC AEGIS - Risk Threshold Alert",
            "nodes": [
                {
                    "name": "Webhook Trigger",
                    "type": "n8n-nodes-base.webhook",
                    "parameters": {"path": "aegis-risk"},
                },
                {
                    "name": "Condition Check",
                    "type": "n8n-nodes-base.if",
                    "parameters": {
                        "conditions": {
                            "number": [
                                {
                                    "value1": "={{ $json.risk_score }}",
                                    "operation": "largerEqual",
                                    "value2": 80,
                                },
                            ],
                        },
                    },
                },
                {
                    "name": "High Risk Action",
                    "type": "n8n-nodes-base.webhook",
                    "parameters": {"url": "{{ $json.escalation_webhook }}"},
                },
            ],
        }

