# 🛡️ QUBIC AEGIS - Predictive AI Multi-Agent Security & Risk Intelligence & Trading Intelligence System for Qubic Blockchain

**Version 2.1** - Production-Ready Security & Trading Intelligence System for Qubic Blockchain

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [AI Features](#ai-features)
- [Testing](#testing)
- [Deployment](#deployment)

---

## 🎯 Overview

**QUBIC AEGIS** is an advanced AI-powered multi-agent security system designed for the Qubic blockchain. It provides real-time transaction analysis, risk assessment, predictive analytics, and automated threat response using cutting-edge AI technology.

### Key Capabilities

- 🔍 **Real-time Transaction Monitoring** via WebSocket
- 🧠 **AI-Powered Risk Analysis** using Groq (Llama-3.3-70b)
- 📊 **Market Intelligence** for Qubic tokens
- 🚨 **Adaptive Threat Detection** (DEFCON mode)
- 🛡️ **Active Defense** simulation (Layer 1 ready)
- 📈 **Predictive Risk Forecasting**
- 💬 **Explainable AI (XAI)** for transparency
- 🎯 **Trading Signals** for institutional traders

---

## ✨ Features

### Core Security Features

1. **Multi-Agent AI System**

   - **Agent Collector**: Extracts transaction features
   - **Agent Risk Analyst**: Real LLM-powered risk analysis
   - **Agent Predictor**: Forecasting future risks
   - **Agent Simulator**: Attack scenario simulation
   - **Agent Automator**: n8n/EasyConnect integration

2. **Adaptive Thresholds (DEFCON Mode)** 🚨

   - Automatically adjusts alert sensitivity based on attack frequency
   - DEFCON 5 (Normal) → DEFCON 1 (Maximum Alert)
   - Dynamic threshold adjustment (80 → 50 when under heavy attack)
   - Real-time status via `/api/defcon-status`

3. **Active Defense** 🛡️

   - Simulated firewall blocks for CRITICAL risks
   - Layer 1 integration ready
   - Automatic mitigation steps
   - Status tracking and logging

4. **Sentiment Analysis** 💭
   - Correlates on-chain activity with social sentiment
   - Mocked for demo (ready for real API integration)
   - Twitter/Discord/Reddit mentions tracking
   - Risk-sentiment correlation analysis

### Market Intelligence (V2)

5. **Token Tracking**

   - Real-time tracking of Qubic tokens (QX, QXALPHA, etc.)
   - Risk scores per token
   - 24h statistics and trends
   - Liquidity and volume analysis

6. **Trading Signals**
   - Automatic signal generation for HIGH/CRITICAL risks
   - Whale activity detection
   - Volume spike alerts
   - Suspicious cluster identification

### Predictive Analytics

7. **Risk Forecasting**

   - Per-wallet risk predictions
   - Global network risk trends
   - Exponential Moving Average (EMA) algorithms
   - Confidence scoring

8. **Attack Simulation**
   - Multiple scenario types (whale_dump, wash_trade, flash_attack, etc.)
   - Step-by-step attack breakdown
   - AI-generated recommendations
   - Impact estimation

### Explainable AI (XAI)

9. **Transparent Decision Making**
   - AI-generated explanations for every risk assessment
   - Structured risk factors
   - Confidence levels
   - Actionable recommendations

---

## 🏗️ Architecture

```
backend/
├── app/
│   ├── agents/              # AI Agents
│   │   ├── agent_collector.py
│   │   ├── agent_risk_analyst.py    # Real LLM-powered
│   │   ├── agent_predictor.py       # EMA forecasting
│   │   ├── agent_simulator.py       # Attack scenarios
│   │   ├── agent_automator.py       # n8n integration
│   │   └── multi_agent_orchestrator.py  # Main coordinator
│   ├── core/
│   │   ├── ai_brain.py              # Groq integration
│   │   └── ai_brain_langchain.py    # LangChain alternative
│   ├── models/
│   │   ├── transaction.py           # Transaction model
│   │   ├── events.py                # RiskEvent model
│   │   └── market.py                # TokenStats, TokenSignal
│   ├── services/
│   │   ├── mock_generator.py        # Transaction generator (V2: with tokens)
│   │   ├── qubic_simulation.py      # Realistic Qubic simulation
│   │   ├── qubic_data_replay.py     # Replay real data
│   │   ├── market_intel.py          # Market Intelligence service
│   │   └── test_data_generator.py   # Test data generation
│   ├── api/
│   │   └── routes.py                # All API endpoints
│   └── config.py                    # Configuration
├── tests/
│   └── verify_v2.py                 # Market Intelligence tests
├── check_groq_setup.py              # Groq verification script
├── init_test_data.py                # Initialize test data
├── main.py                          # FastAPI app entry
├── requirements.txt
└── .env                             # Environment variables
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip
- Groq API key (optional but recommended)

### Installation

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env  # Or create manually
# Edit .env and add your GROQ_API_KEY

# 3. Verify Groq setup (optional)
python check_groq_setup.py

# 4. Initialize test data (optional)
python init_test_data.py

# 5. Start the server
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# AI Configuration
GROQ_API_KEY=gsk_your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile  # Options: llama-3.3-70b-versatile, llama-3.1-70b-versatile, mixtral-8x7b-32768

# Qubic Network
QUBIC_RPC_URL=https://api.qubic.org
QUBIC_REALISTIC_MODE=true  # Use realistic Qubic simulation

# n8n Integration
N8N_WEBHOOK_URL=https://your-n8n-webhook-url

# Data Streaming
MOCK_DATA_INTERVAL=2.0  # Seconds between transactions

# Risk Engine Configuration
RISK_BASELINE_AMOUNT=10000.0
RISK_ACTIVITY_WINDOW_MINUTES=10
RISK_WHALE_THRESHOLD=50000.0
```

### Getting Groq API Key

1. Visit https://console.groq.com/
2. Sign up / Log in
3. Go to "API Keys"
4. Create a new API key
5. Add it to `.env` as `GROQ_API_KEY`

### Verify Groq Configuration

```bash
python check_groq_setup.py
```

This script will:

- Check for `.env` file in multiple locations
- Verify `GROQ_API_KEY` is set
- Test Groq API connection
- Provide troubleshooting tips

---

## 📡 API Endpoints

### WebSocket

#### `WS /ws/monitor`

Real-time transaction monitoring stream.

**Message Format**:

```json
{
  "type": "transaction_analysis",
  "data": {
    "transaction": {...},
    "risk_score": 75.5,
    "risk_level": "HIGH",
    "explanation": "...",
    "prediction": {...},
    "defcon_status": {
      "defcon_level": 3,
      "alert_threshold": 70.0,
      "attacks_last_minute": 3
    },
    "sentiment_analysis": {
      "sentiment_label": "BEARISH",
      "correlation_with_risk": "CONFIRMED"
    },
    "active_defense": {
      "action": "FIREWALL_BLOCK",
      "status": "SENT_TO_NODE"
    }
  }
}
```

---

### REST Endpoints

#### Health & Status

- **`GET /api/health`** - Health check
- **`GET /api/defcon-status`** - Current DEFCON level and adaptive threshold status

#### Market Intelligence (V2)

- **`GET /api/market-intel/overview`** - Combined tokens overview and signals
- **`GET /api/tokens`** - All tracked tokens with stats
- **`GET /api/tokens/{symbol}`** - Specific token details (e.g., `/api/tokens/QXALPHA`)
- **`GET /api/signals`** - Recent trading/security signals

#### Predictions & Forecasting

- **`GET /api/predict`** - Risk predictions
  - Query params: `horizon` (short_term/medium_term/long_term), `wallet_id` (optional)

#### Attack Simulation

- **`POST /api/simulate`** - Simulate attack scenario
  - Body: `{ "scenario_type": "whale_dump", "parameters": {...} }`
  - Scenarios: `whale_dump`, `wash_trade`, `flash_attack`, `wallet_drain`, `spam_attack`, `liquidity_manipulation`

#### Wallet Analysis

- **`GET /api/wallet-graph`** - Wallet interaction graph
  - Query params: `max_nodes` (default: 50)
- **`GET /api/wallet/{wallet_id}`** - Specific wallet analysis

#### AI Chat

- **`POST /api/ask-aegis`** - Chat with AI security copilot
  - Body: `{ "message": "Your question", "context": {...} }`

#### Automation

- **`POST /api/trigger-automation`** - Trigger n8n webhook
  - Body: `{ "webhook_url": "...", "message": "..." }`
- **`POST /api/trigger-automation-riskevent`** - Trigger with RiskEvent model
  - Body: `{ "risk_event": {...}, "webhook_url": "..." }`

---

## 🧠 AI Features

### Real AI Analysis (Groq)

The system uses **Groq** with **Llama-3.3-70b-versatile** for real-time, intelligent transaction analysis.

**Features**:

- Context-aware risk assessment
- Behavioral pattern detection
- Explainable decisions (XAI)
- Technical threat analysis
- Intelligent recommendations

**Prompt Engineering**:

- Specialized prompts for Qubic blockchain security
- Context-rich analysis (wallet history, patterns, tokens)
- Structured JSON output for reliability

### Fallback Mode

If Groq is not configured, the system uses rule-based analysis with high-quality heuristics. However, **real AI is strongly recommended** for best results.

---

## 🚨 DEFCON Mode (Adaptive Thresholds)

The system automatically adapts its sensitivity based on attack frequency:

| DEFCON Level | Attacks/min | Alert Threshold | Status              |
| ------------ | ----------- | --------------- | ------------------- |
| **DEFCON 5** | 0           | 80              | Normal Operations   |
| **DEFCON 4** | 1+          | 75              | Increased Readiness |
| **DEFCON 3** | 3+          | 70              | Elevated Alert      |
| **DEFCON 2** | 5+          | 60              | High Alert          |
| **DEFCON 1** | 10+         | 50              | Maximum Alert       |

**How it works**:

- Tracks high-risk events (HIGH/CRITICAL) with timestamps
- Calculates attack frequency in last 60 seconds
- Automatically adjusts DEFCON level and alert threshold
- Risk levels are upgraded in high-alert modes

**API**: `GET /api/defcon-status` - Returns current DEFCON level and status

---

## 🛡️ Active Defense

For CRITICAL risk events, the system simulates active defense actions:

**Simulated Actions**:

- `FIREWALL_BLOCK` - Block command sent to network nodes
- Status: `SENT_TO_NODE`
- Mitigation steps logged
- Ready for real Layer 1 integration

**When Triggered**:

- Risk level = CRITICAL
- Automatic for all CRITICAL events
- Included in automation payloads

**Future**: Ready for real Qubic node integration for actual transaction blocking.

---

## 💭 Sentiment Analysis

The system correlates on-chain activity with social sentiment:

**Features**:

- Sentiment score: -1.0 (bearish) to +1.0 (bullish)
- Social mentions: Twitter, Discord, Reddit
- Correlation analysis: CONFIRMED, PARTIAL, DIVERGENT, UNCERTAIN

**Current Status**: Mocked for demo, structure ready for real API integration

**Integration Ready**: Twitter API, Discord API, Reddit API

---

## 📊 Market Intelligence (V2)

### Token Tracking

Tracks all tokens mentioned in transactions:

- Risk scores per token
- 24h statistics (alerts, average risk)
- Trend analysis (UP/DOWN/STABLE)
- Liquidity tags and risk labels

### Trading Signals

Automatic signal generation:

- **WHALE_DUMP_RISK**: Large sell orders detected
- **VOLUME_SPIKE**: Unusual volume increase
- **SUSPICIOUS_CLUSTER**: Coordinated activity patterns

**Signal Criteria**: HIGH/CRITICAL risk events automatically generate signals

### Token Distribution (Mock Data)

- **30%** QXALPHA (demo token)
- **25%** QX
- **15%** Other tokens (CFB, QTRY)
- **30%** No token (simple QUBIC transfers)

---

## 🧪 Testing

### Quick Test

```bash
# Start backend
uvicorn main:app --reload

# In another terminal, test endpoints
curl http://localhost:8000/api/health
curl http://localhost:8000/api/defcon-status
curl http://localhost:8000/api/market-intel/overview
```

### Comprehensive Testing

```bash
# Run Market Intelligence tests
python tests/verify_v2.py
```

This script tests:

- Market Intelligence endpoints
- Token tracking
- Signal generation
- Data accumulation

### Test with Frontend

1. Start backend: `uvicorn main:app --reload`
2. Start frontend: `cd ../frontend && npm run dev`
3. Open http://localhost:5173
4. Verify WebSocket connection (badge should show "ONLINE")
5. Test all pages and features

---

## 📈 API Documentation

Interactive API documentation available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔧 Development

### Project Structure

- **Agents**: Modular AI agents for different tasks
- **Core**: Core AI brain and intelligence engine
- **Models**: Pydantic models for type safety
- **Services**: Business logic (mock generation, market intel, etc.)
- **API**: FastAPI routes and WebSocket handlers

### Adding New Features

1. **New Agent**: Add to `app/agents/`
2. **New Model**: Add to `app/models/`
3. **New Endpoint**: Add to `app/api/routes.py`
4. **New Service**: Add to `app/services/`

### Code Quality

- Type hints everywhere
- Docstrings for all functions
- Error handling and logging
- Backward compatibility maintained

---

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Use secure secret management
2. **CORS**: Restrict origins in production
3. **Rate Limiting**: Add rate limiting for API endpoints
4. **Monitoring**: Add logging and monitoring
5. **Database**: Consider persistent storage for production

### Docker (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🎯 Features for Hackathon Demo

### Highlight These Features

1. **Real AI**: Groq Llama-3.3 (not fake, real intelligence)
2. **Adaptive System**: DEFCON mode (auto-adjusts to threats)
3. **Proactive Defense**: Active Defense simulation (Layer 1 ready)
4. **Complete Solution**: Security + Trading Intelligence
5. **Production-Ready**: Clean architecture, extensible
6. **Innovative**: Sentiment Analysis + XAI + Predictions

### Demo Flow

1. Show Dashboard with live transactions
2. Highlight DEFCON adaptation
3. Demonstrate Market Intelligence
4. Show AI Chat capabilities
5. Trigger Active Defense → Discord notification
6. Explain Layer 1 readiness

---

## 📚 Additional Resources

- **Frontend**: See `../frontend/README.md`
- **Testing Guide**: See `TESTING_GUIDE_COMPLETE.md`
- **Groq Setup**: Run `python check_groq_setup.py`
- **API Testing**: See `TEST_APIS_POWERSHELL.md` (if exists)

---

## 🐛 Troubleshooting

### Groq Not Working

```bash
# 1. Check .env file
cat backend/.env | grep GROQ_API_KEY

# 2. Verify setup
python check_groq_setup.py

# 3. Check logs
# Look for "WARNING: GROQ_API_KEY not found" in backend logs
```

### WebSocket Connection Issues

- Verify backend is running on port 8000
- Check CORS settings in `main.py`
- Verify WebSocket endpoint: `ws://localhost:8000/ws/monitor`
- Check browser console for errors

### Market Intelligence Empty

- Wait 10-20 seconds for data to accumulate
- Verify transactions are being generated
- Check that transactions include `token_symbol`
- Test endpoint: `curl http://localhost:8000/api/market-intel/overview`

---

## 📝 Version History

### v2.1 (Current)

- ✅ Market Intelligence (V2) - Token tracking and signals
- ✅ DEFCON Mode - Adaptive thresholds
- ✅ Active Defense - Simulated firewall blocks
- ✅ Sentiment Analysis - Social correlation
- ✅ Enhanced AI prompts - More context and intelligence
- ✅ Improved error handling - Robust Groq integration

### v2.0

- Multi-agent system
- Real AI analysis (Groq)
- Predictive analytics
- Attack simulation
- WebSocket streaming

---

## 🤝 Contributing

This is a hackathon project, but contributions welcome!

---

## 📄 License

MIT License - Hackathon Project

---

## 🙏 Acknowledgments

- **Groq** for ultra-fast AI inference
- **Qubic** for the amazing blockchain
- **FastAPI** for the excellent framework

---

**Built for the Qubic Hackathon**
