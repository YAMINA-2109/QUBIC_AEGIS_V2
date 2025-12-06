import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.agent_predictor import AgentPredictor

def test_prediction_logic():
    print("🔮 TESTING PREDICTOR AGENT (MATH + AI)...\n")
    
    predictor = AgentPredictor()
    
    # SCENARIO: A progressive attack starting
    # The risk scores are rising over time: 10, 20, 35, 60, 85
    scenario_scores = [10, 20, 35, 60, 85]
    
    print("📈 Simulating rising risk trend: [10 -> 20 -> 35 -> 60 -> 85]")
    
    final_prediction = {}
    
    # Feed the data point by point
    for score in scenario_scores:
        final_prediction = predictor.predict_future_risk(score)
        print(f"   Input: {score} -> Trend: {final_prediction['trend_direction']}")

    print("\n--- 🔮 AEGIS FORECAST REPORT ---")
    print(f"📈 Trend:             {final_prediction['trend_direction']}")
    print(f"🎯 Predicted (1h):    {final_prediction['predicted_risk_1h']}/100")
    print(f"🗣️ AI Narrative:      \"{final_prediction['forecast_narrative']}\"")
    print("----------------------------------\n")
    
    # Validation
    if final_prediction['predicted_risk_1h'] > 85:
        print("✅ SUCCESS: Predictor correctly forecasted the rising danger!")
    else:
        print("❌ FAILURE: Predictor failed to see the trend.")

if __name__ == "__main__":
    test_prediction_logic()