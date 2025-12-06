"""
Agent Simulator - Attack Simulation Engine
Simulates various attack scenarios and their impacts
Enhanced with step-by-step simulations and LLM-generated recommendations
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random


class AgentSimulator:
    """
    Simulates attack scenarios to understand potential impacts
    """
    
    def __init__(self, ai_brain: Optional[Any] = None):
        """
        Initialize the simulator
        
        Args:
            ai_brain: Optional AegisBrain instance for LLM-generated recommendations
        """
        self.simulation_scenarios = {
            "whale_dump": self._simulate_whale_dump,
            "wash_trade": self._simulate_wash_trading,  # Updated key
            "flash_attack": self._simulate_flash_loan,  # Updated key
            "wallet_drain": self._simulate_wallet_drain,  # New scenario
            "spam_attack": self._simulate_spam,
            "liquidity_manipulation": self._simulate_liquidity_manipulation,
        }
        self.ai_brain = ai_brain
    
    async def simulate(self, scenario_type: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run a simulation with step-by-step breakdown
        
        Args:
            scenario_type: Type of attack scenario
            parameters: Optional parameters for the simulation
            
        Returns:
            Simulation results with steps, peak_risk, estimated_impact, and LLM recommendation
        """
        if scenario_type not in self.simulation_scenarios:
            return {
                "error": f"Unknown scenario type: {scenario_type}",
                "available_scenarios": list(self.simulation_scenarios.keys()),
            }
        
        simulator_func = self.simulation_scenarios[scenario_type]
        result = simulator_func(parameters or {})
        
        # Generate LLM recommendation if AI brain is available
        if self.ai_brain:
            try:
                recommendation = await self._generate_llm_recommendation(scenario_type, result)
                result["aegis_recommendation"] = recommendation
            except Exception as e:
                result["aegis_recommendation"] = f"AI recommendation generation failed: {str(e)}"
        else:
            result["aegis_recommendation"] = result.get("recommendations", ["Manual review recommended"])[0]
        
        return result
    
    async def _generate_llm_recommendation(self, scenario_type: str, simulation_result: Dict[str, Any]) -> str:
        """Generate LLM-powered recommendation for the simulation"""
        if not self.ai_brain or not self.ai_brain.client:
            return "AI analysis unavailable"
        
        prompt = f"""You are AEGIS, an AI security expert for Qubic blockchain.

A {scenario_type} attack scenario was simulated with these results:
- Peak Risk: {simulation_result.get('peak_risk', 'N/A')}
- Estimated Impact: {simulation_result.get('estimated_impact', 'N/A')}
- Steps: {len(simulation_result.get('steps', []))}

Provide a concise, technical recommendation (max 200 words) on:
1. Immediate mitigation actions
2. Detection strategies
3. Prevention measures
4. Network impact assessment

Be specific and actionable."""

        try:
            response = self.ai_brain.client.chat.completions.create(
                model=self.ai_brain.model,
                messages=[
                    {"role": "system", "content": "You are AEGIS, an expert AI security analyst for Qubic blockchain."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating recommendation: {str(e)}"
    
    def _simulate_whale_dump(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate a whale dumping scenario with step-by-step breakdown"""
        amount = params.get("amount", 1000000)
        duration_minutes = params.get("duration_minutes", 30)
        tick_start = params.get("tick_start", 8923456)
        
        # Generate step-by-step simulation
        steps = []
        peak_risk = 0
        affected_wallets = []
        
        # Step 1: Initial detection
        steps.append({
            "tick": tick_start,
            "description": f"Large transaction detected: {amount * 0.3:,.0f} QUBIC from whale wallet",
            "affected_wallets": ["whale_wallet_1"],
            "risk_score": 75.0
        })
        peak_risk = max(peak_risk, 75.0)
        affected_wallets.extend(["whale_wallet_1"])
        
        # Step 2: Escalation
        steps.append({
            "tick": tick_start + 100,
            "description": f"Accelerated dumping: {amount * 0.5:,.0f} QUBIC in rapid succession",
            "affected_wallets": ["whale_wallet_1", "exchange_1", "exchange_2"],
            "risk_score": 90.0
        })
        peak_risk = max(peak_risk, 90.0)
        affected_wallets.extend(["exchange_1", "exchange_2"])
        
        # Step 3: Peak impact
        steps.append({
            "tick": tick_start + 200,
            "description": f"Peak dumping phase: {amount * 0.2:,.0f} QUBIC causing market disruption",
            "affected_wallets": list(set(affected_wallets + ["liquidity_pool_1", "trader_1", "trader_2"])),
            "risk_score": 95.0
        })
        peak_risk = max(peak_risk, 95.0)
        
        # Simulate impact
        impact_on_price = -random.uniform(5, 15)  # % price drop
        
        return {
            "scenario": "whale_dump",
            "steps": steps,
            "peak_risk": peak_risk,
            "estimated_impact": "High" if peak_risk >= 85 else "Medium" if peak_risk >= 60 else "Low",
            "description": f"Simulated whale dumping {amount:,.0f} QUBIC over {duration_minutes} minutes",
            "impact_details": {
                "price_impact_percent": round(impact_on_price, 2),
                "affected_wallets_count": len(set(affected_wallets)),
                "market_confidence_drop": round(abs(impact_on_price) * 2, 2),
            },
            "recommendations": [
                "Alert community immediately",
                "Monitor wallet movements closely",
                "Prepare liquidity buffer",
            ],
        }
    
    def _simulate_wash_trading(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate wash trading scenario with step-by-step breakdown"""
        transaction_count = params.get("transaction_count", 100)
        wallet_pairs = params.get("wallet_pairs", 10)
        tick_start = params.get("tick_start", 8923456)
        
        steps = []
        affected_wallets = [f"wallet_pair_{i}_a" for i in range(wallet_pairs)] + [f"wallet_pair_{i}_b" for i in range(wallet_pairs)]
        
        # Step 1: Initial pattern
        steps.append({
            "tick": tick_start,
            "description": f"Circular transaction pattern detected: {wallet_pairs} wallet pairs identified",
            "affected_wallets": affected_wallets[:5],
            "risk_score": 60.0
        })
        
        # Step 2: Escalation
        steps.append({
            "tick": tick_start + 50,
            "description": f"Wash trading intensifies: {transaction_count // 2} transactions in rapid succession",
            "affected_wallets": affected_wallets,
            "risk_score": 80.0
        })
        
        # Step 3: Peak
        steps.append({
            "tick": tick_start + 100,
            "description": f"Peak wash trading activity: {transaction_count} total transactions, {transaction_count * random.uniform(1000, 10000):,.0f} QUBIC fake volume",
            "affected_wallets": affected_wallets,
            "risk_score": 85.0
        })
        
        return {
            "scenario": "wash_trade",
            "steps": steps,
            "peak_risk": 85.0,
            "estimated_impact": "High",
            "description": f"Simulated wash trading with {transaction_count} transactions across {wallet_pairs} wallet pairs",
            "impact_details": {
                "fake_volume_generated": transaction_count * random.uniform(1000, 10000),
                "market_manipulation_score": 85,
                "detection_difficulty": "high",
            },
            "recommendations": [
                "Use graph analysis to detect circular transactions",
                "Implement wallet clustering detection",
                "Cross-reference with historical patterns",
            ],
        }
    
    def _simulate_flash_loan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate flash loan attack with step-by-step breakdown"""
        loan_amount = params.get("loan_amount", 500000)
        tick_start = params.get("tick_start", 8923456)
        
        steps = []
        
        # Step 1: Flash loan initiation
        steps.append({
            "tick": tick_start,
            "description": f"Flash loan initiated: {loan_amount:,.0f} QUBIC borrowed instantly",
            "affected_wallets": ["attacker_wallet", "liquidity_pool_1"],
            "risk_score": 70.0
        })
        
        # Step 2: Exploitation
        steps.append({
            "tick": tick_start + 1,
            "description": f"Price manipulation detected: Arbitrage opportunity exploited across {random.randint(2, 5)} DEX pools",
            "affected_wallets": ["attacker_wallet", "liquidity_pool_1", "liquidity_pool_2", "dex_1"],
            "risk_score": 95.0
        })
        
        # Step 3: Repayment
        steps.append({
            "tick": tick_start + 2,
            "description": f"Flash loan repaid: Attack completed in {2} blocks, estimated profit {random.uniform(10000, 50000):,.0f} QUBIC",
            "affected_wallets": ["attacker_wallet", "liquidity_pool_1"],
            "risk_score": 90.0
        })
        
        return {
            "scenario": "flash_attack",
            "steps": steps,
            "peak_risk": 95.0,
            "estimated_impact": "Critical",
            "description": f"Simulated flash loan attack with {loan_amount:,.0f} QUBIC",
            "impact_details": {
                "potential_profit_for_attacker": random.uniform(10000, 50000),
                "liquidity_pool_impact": "high",
                "price_manipulation_window": "1-2 blocks",
            },
            "recommendations": [
                "Implement real-time liquidity monitoring",
                "Set maximum transaction limits per block",
                "Use time-weighted average price (TWAP) mechanisms",
            ],
        }
    
    def _simulate_wallet_drain(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate wallet drain attack with step-by-step breakdown"""
        victim_wallets = params.get("victim_wallets", ["victim_1", "victim_2"])
        tick_start = params.get("tick_start", 8923456)
        total_drained = params.get("total_drained", 100000)
        
        steps = []
        
        # Step 1: Initial compromise
        steps.append({
            "tick": tick_start,
            "description": f"Security breach detected: {len(victim_wallets)} wallets compromised",
            "affected_wallets": victim_wallets + ["attacker_wallet"],
            "risk_score": 85.0
        })
        
        # Step 2: Drain execution
        steps.append({
            "tick": tick_start + 10,
            "description": f"Active draining: {total_drained:,.0f} QUBIC being transferred to attacker wallet",
            "affected_wallets": victim_wallets + ["attacker_wallet", "mixer_relay"],
            "risk_score": 98.0
        })
        
        # Step 3: Obfuscation
        steps.append({
            "tick": tick_start + 20,
            "description": f"Funds routed through mixer: Transaction obfuscation in progress",
            "affected_wallets": ["attacker_wallet", "mixer_relay", "destination_wallet"],
            "risk_score": 92.0
        })
        
        return {
            "scenario": "wallet_drain",
            "steps": steps,
            "peak_risk": 98.0,
            "estimated_impact": "Critical",
            "description": f"Simulated wallet drain attack affecting {len(victim_wallets)} wallets, {total_drained:,.0f} QUBIC stolen",
            "impact_details": {
                "total_drained": total_drained,
                "victims_count": len(victim_wallets),
                "recovery_probability": "low",
            },
            "recommendations": [
                "Immediately freeze affected wallets",
                "Alert all exchanges to block attacker addresses",
                "Coordinate with law enforcement",
            ],
        }
    
    def _simulate_spam(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate spam attack"""
        spam_rate = params.get("spam_rate", 100)  # transactions per second
        
        return {
            "scenario": "spam_attack",
            "description": f"Simulated spam attack at {spam_rate} transactions/second",
            "estimated_impact": {
                "network_congestion": "high",
                "transaction_processing_delay": f"{random.uniform(10, 30):.1f} seconds",
                "gas_price_increase": f"{random.uniform(50, 200):.1f}%",
            },
            "propagation": {
                "affected_blocks": random.randint(10, 50),
                "legitimate_transaction_delay": "15-45 seconds",
            },
            "recommendations": [
                "Implement rate limiting per wallet",
                "Increase minimum transaction fee",
                "Prioritize high-value transactions",
            ],
        }
    
    def _simulate_liquidity_manipulation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate liquidity manipulation"""
        manipulation_amount = params.get("amount", 250000)
        
        return {
            "scenario": "liquidity_manipulation",
            "description": f"Simulated liquidity manipulation with {manipulation_amount:,.0f} QUBIC",
            "estimated_impact": {
                "price_impact": round(random.uniform(10, 25), 2),
                "liquidity_pool_distortion": "high",
                "arbitrage_opportunities": "high",
            },
            "propagation": {
                "affected_dexes": random.randint(2, 5),
                "cascade_effect": "medium-high",
            },
            "recommendations": [
                "Monitor multiple liquidity pools simultaneously",
                "Implement circuit breakers",
                "Alert DEX operators",
            ],
        }

