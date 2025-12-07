"""
Agent Predictor (V2 - Expert Edition)
Capabilities:
- Time-Series Forecasting using EMA (Exponential Moving Average)
- AI-based Narrative Forecasting (Groq)
- Trend Direction Analysis (UP/DOWN/STABLE)
"""
import os
import numpy as np
from typing import Dict, Any, List
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class AgentPredictor:
    """
    The 'Oracle' of Aegis.
    Predicts future risk levels based on historical trend lines and AI intuition.
    """
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        # Using the versatile model as verified working
        self.model = os.getenv("GROQ_MODEL")
        
        # Local memory for risk history (Simulating a Time-Series DB)
        # Format: List of risk scores [10, 20, 45, 80...]
        self.risk_history: List[int] = []

    def calculate_ema(self, data: List[int], window: int = 5) -> float:
        """
        Calculates Exponential Moving Average to detect rapid trend changes.
        """
        if not data:
            return 0.0
        if len(data) < window:
            return float(np.mean(data))
            
        weights = np.exp(np.linspace(-1., 0., window))
        weights /= weights.sum()
        
        # Take the last 'window' elements
        recent_data = data[-window:]
        ema = np.dot(recent_data, weights)
        return float(ema)

    def predict_future_risk(self, current_risk: int) -> Dict[str, Any]:
        """
        Main prediction logic.
        Combines Math (EMA) + AI (LLM) to forecast risk.
        """
        # 1. Update History
        self.risk_history.append(current_risk)
        if len(self.risk_history) > 20:
            self.risk_history.pop(0) # Keep sliding window
            
        # 2. Mathematical Trend Analysis
        ema_short = self.calculate_ema(self.risk_history, window=3)
        ema_long = self.calculate_ema(self.risk_history, window=10)
        
        trend = "STABLE"
        if ema_short > ema_long + 5:
            trend = "UP RAPIDLY"
        elif ema_short > ema_long:
            trend = "UP"
        elif ema_short < ema_long - 5:
            trend = "DOWN"

        # 3. AI Narrative Forecast
        # We only ask AI if the trend is moving, to explain WHY.
        ai_forecast = "Market stability expected."
        
        if trend in ["UP", "UP RAPIDLY"] or current_risk > 50:
            prompt = f"""
            You are a Financial Risk Forecaster for Qubic Blockchain.
            
            DATA:
            - Recent Risk Scores (last 5 mins): {self.risk_history[-5:]}
            - Current Trend: {trend}
            - Current Score: {current_risk}
            
            TASK:
            Predict the risk level for the next 1 hour.
            Write a SHORT forecast sentence (e.g., "Risk likely to peak at 90 due to cascading sell pressure").
            """
            
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=30
                )
                ai_forecast = completion.choices[0].message.content.strip()
            except Exception:
                ai_forecast = "Forecast model unavailable."

        # 4. Quantitative Prediction (Next Hour)
        # Simple projection based on momentum
        momentum = ema_short - ema_long
        predicted_score = min(100, max(0, current_risk + (momentum * 1.5)))

        return {
            "trend_direction": trend,
            "predicted_risk_1h": round(predicted_score, 1),
            "forecast_narrative": ai_forecast,
            "confidence_score": 85 if len(self.risk_history) > 5 else 40
        }