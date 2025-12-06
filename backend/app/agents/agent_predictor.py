"""
Agent Predictor - Predictive Risk Engine
Predicts future risk scores and behaviors
Enhanced with per-wallet history and forecasting
"""
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import deque
import numpy as np


class AgentPredictor:
    """
    Predicts future risk scores and potential dangerous behaviors
    Uses time series analysis and pattern recognition
    """
    
    def __init__(self):
        """Initialize the predictor"""
        self.historical_data: List[Dict[str, Any]] = []
        self.prediction_models = {
            "short_term": None,  # 1 hour
            "medium_term": None,  # 24 hours
            "long_term": None,    # 7 days
        }
        # Per-wallet history: Dict[wallet_id, Deque[(datetime, risk_score)]]
        self.wallet_history: Dict[str, deque] = {}
        self.max_history_length = 200
    
    def add_data_point(self, timestamp: datetime, risk_score: float, transaction_data: Dict[str, Any]):
        """
        Add a data point to the historical dataset
        
        Args:
            timestamp: When the risk was calculated
            risk_score: Risk score (0-100)
            transaction_data: Associated transaction data
        """
        self.historical_data.append({
            "timestamp": timestamp,
            "risk_score": risk_score,
            "transaction_data": transaction_data,
        })
        
        # Keep last 1000 data points
        if len(self.historical_data) > 1000:
            self.historical_data = self.historical_data[-1000:]
    
    def add_wallet_data_point(self, wallet_id: str, risk_score: float) -> None:
        """
        Add a data point to a specific wallet's history
        
        Args:
            wallet_id: Wallet identifier
            risk_score: Risk score (0-100)
        """
        if wallet_id not in self.wallet_history:
            self.wallet_history[wallet_id] = deque(maxlen=self.max_history_length)
        
        self.wallet_history[wallet_id].append((datetime.now(), risk_score))
    
    def predict_risk(self, horizon: str = "short_term") -> Dict[str, Any]:
        """
        Predict future risk score
        
        Args:
            horizon: "short_term" (1h), "medium_term" (24h), or "long_term" (7d)
            
        Returns:
            Prediction dictionary with forecasted risk and confidence
        """
        if len(self.historical_data) < 10:
            return {
                "predicted_risk": 0,
                "confidence": 0,
                "trend": "insufficient_data",
                "forecast": [],
            }
        
        # Extract recent risk scores
        recent_scores = [d["risk_score"] for d in self.historical_data[-50:]]
        
        # Simple moving average prediction
        if horizon == "short_term":
            # Predict 1 hour ahead (assuming 2s intervals, ~1800 points per hour)
            window = 10
            forecast_points = 60  # ~2 minutes ahead
        elif horizon == "medium_term":
            window = 50
            forecast_points = 720  # ~24 minutes ahead (compressed for demo)
        else:  # long_term
            window = 100
            forecast_points = 2100  # ~70 minutes ahead (compressed for demo)
        
        # Moving average
        ma = np.mean(recent_scores[-window:]) if len(recent_scores) >= window else np.mean(recent_scores)
        
        # Trend detection
        if len(recent_scores) >= 10:
            recent_trend = np.polyfit(range(len(recent_scores[-10:])), recent_scores[-10:], 1)[0]
            trend_direction = "increasing" if recent_trend > 0.5 else "decreasing" if recent_trend < -0.5 else "stable"
        else:
            trend_direction = "stable"
        
        # Generate forecast points
        forecast = []
        current_score = recent_scores[-1] if recent_scores else ma
        for i in range(forecast_points):
            # Apply trend with some randomness
            noise = np.random.normal(0, 2)
            predicted = current_score + (recent_trend * (i / forecast_points)) + noise
            predicted = max(0, min(100, predicted))
            forecast.append(predicted)
        
        # Calculate confidence based on data stability
        if len(recent_scores) >= 20:
            std_dev = np.std(recent_scores[-20:])
            confidence = max(0, min(100, 100 - (std_dev * 2)))
        else:
            confidence = 50
        
        return {
            "predicted_risk": float(np.mean(forecast[:10])),  # Average of next few points
            "confidence": float(confidence),
            "trend": trend_direction,
            "forecast": [float(f) for f in forecast[:100]],  # Limit to 100 points for frontend
            "horizon": horizon,
        }
    
    def predict_wallet_behavior(self, wallet_features: Dict[str, Any], historical_patterns: List[Dict]) -> Dict[str, Any]:
        """
        Predict if a wallet will exhibit dangerous behavior
        
        Args:
            wallet_features: Features of the wallet
            historical_patterns: Historical behavior patterns
            
        Returns:
            Behavior prediction dictionary
        """
        # Risk indicators
        risk_indicators = []
        risk_score = 0
        
        # High frequency trading
        if wallet_features.get("frequency", 0) > 10:  # > 10 tx/hour
            risk_indicators.append("High transaction frequency detected")
            risk_score += 20
        
        # Large volume
        if wallet_features.get("total_volume", 0) > 100000:
            risk_indicators.append("Large transaction volume")
            risk_score += 15
        
        # Many unique counterparts (potential mixing)
        if wallet_features.get("unique_counterparts", 0) > 50:
            risk_indicators.append("Unusual number of counterparties")
            risk_score += 10
        
        # Sudden spike detection
        if historical_patterns:
            recent_volume = sum(p.get("volume", 0) for p in historical_patterns[-5:])
            older_volume = sum(p.get("volume", 0) for p in historical_patterns[-20:-5])
            if older_volume > 0 and recent_volume > older_volume * 3:
                risk_indicators.append("Sudden volume spike detected")
                risk_score += 25
        
        return {
            "predicted_behavior": "high_risk" if risk_score > 40 else "moderate_risk" if risk_score > 20 else "low_risk",
            "risk_score": min(100, risk_score),
            "indicators": risk_indicators,
            "probability": min(100, risk_score + 20),  # Probability of dangerous behavior
        }
    
    def forecast(self, wallet_id: str) -> Dict[str, Any]:
        """
        Forecast risk for a specific wallet based on its history
        
        Args:
            wallet_id: Wallet identifier
            
        Returns:
            {
                "wallet_id": wallet_id,
                "history": [{timestamp: iso_str, risk_score: float}],
                "forecast": [{timestamp: iso_str, predicted_risk: float}],
                "trend": "UP|DOWN|STABLE"
            }
        """
        if wallet_id not in self.wallet_history or len(self.wallet_history[wallet_id]) < 2:
            return {
                "wallet_id": wallet_id,
                "history": [],
                "forecast": [],
                "trend": "STABLE",
                "error": "Insufficient data"
            }
        
        # Get history
        history_data = list(self.wallet_history[wallet_id])
        
        # Convert to required format
        history = [
            {
                "timestamp": ts.isoformat(),
                "risk_score": float(score)
            }
            for ts, score in history_data
        ]
        
        # Calculate trend using moving average
        if len(history_data) >= 10:
            recent_scores = [score for _, score in history_data[-10:]]
            older_scores = [score for _, score in history_data[-20:-10]] if len(history_data) >= 20 else recent_scores[:5]
            
            recent_avg = np.mean(recent_scores)
            older_avg = np.mean(older_scores)
            
            if recent_avg > older_avg + 5:
                trend = "UP"
            elif recent_avg < older_avg - 5:
                trend = "DOWN"
            else:
                trend = "STABLE"
        else:
            trend = "STABLE"
        
        # Generate forecast using exponential moving average
        scores = [score for _, score in history_data]
        
        # EMA calculation
        alpha = 0.3  # Smoothing factor
        ema = scores[-1] if scores else 0
        for score in scores[-10:]:
            ema = alpha * score + (1 - alpha) * ema
        
        # Generate forecast points (next 30 minutes, assuming 2s intervals = 900 points)
        forecast_points = min(100, 30)  # Limit to 100 for API response
        forecast = []
        
        current_time = datetime.now()
        trend_adjustment = 0.5 if trend == "UP" else (-0.5 if trend == "DOWN" else 0)
        
        for i in range(1, forecast_points + 1):
            predicted_score = ema + (trend_adjustment * i * 0.1)
            predicted_score = max(0.0, min(100.0, predicted_score))  # Clamp to 0-100
            
            forecast_time = current_time + timedelta(seconds=i * 2)  # 2s intervals
            
            forecast.append({
                "timestamp": forecast_time.isoformat(),
                "predicted_risk": float(predicted_score)
            })
        
        return {
            "wallet_id": wallet_id,
            "history": history,
            "forecast": forecast,
            "trend": trend
        }

