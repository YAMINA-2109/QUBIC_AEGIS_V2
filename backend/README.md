# QUBIC AEGIS Backend

**Version 2.1** - Production-Ready Multi-Agent AI Security & Risk Intelligence System

---

## Overview

**QUBIC AEGIS Backend** is an advanced AI-powered multi-agent security system designed for the Qubic blockchain. It provides real-time transaction analysis, risk assessment, predictive analytics, automated threat response, and comprehensive smart contract auditing using cutting-edge AI technology.

### Key Capabilities

- **Real-time Transaction Monitoring** via WebSocket
- **AI-Powered Risk Analysis** using Groq (Llama-3.3-70b-versatile)
- **Market Intelligence** for Qubic tokens
- **Adaptive Threat Detection** (DEFCON mode)
- **Active Defense** simulation (Layer 1 ready)
- **Predictive Risk Forecasting**
- **Explainable AI (XAI)** for transparency
- **Trading Signals** for institutional traders
- **Smart Contract Auditing** via integrated SmartGuard Core

---

## Features

### Core Security Features

#### 1. Multi-Agent AI System

- **Agent Collector**: Extracts transaction features and patterns
- **Agent Risk Analyst**: Real LLM-powered risk analysis using Groq
- **Agent Predictor**: Forecasting future risks with EMA algorithms
- **Agent Simulator**: Attack scenario simulation and analysis
- **Agent Automator**: n8n/EasyConnect integration for active defense

#### 2. Adaptive Thresholds (DEFCON Mode)

Automatically adjusts alert sensitivity based on attack frequency:

| DEFCON Level | Attacks/min | Alert Threshold | Status              |
| ------------ | ----------- | --------------- | ------------------- |
| **DEFCON 5** | 0           | 80              | Normal Operations   |
| **DEFCON 4** | 1+          | 75              | Increased Readiness |
| **DEFCON 3** | 1+          | 70              | Elevated Alert      |
| **DEFCON 2** | 2+          | 60              | High Alert          |
| **DEFCON 1** | 3+          | 50              | Maximum Alert       |

**How it works**:

- Tracks high-risk events (HIGH/CRITICAL) with timestamps
- Calculates attack frequency in last 60 seconds
- Automatically adjusts DEFCON level and alert threshold
- Risk levels are upgraded in high-alert modes

#### 3. Active Defense

For CRITICAL risk events, the system simulates active defense actions:

- `FIREWALL_BLOCK` - Block command sent to network nodes
- Status: `SENT_TO_NODE`
- Mitigation steps logged
- Ready for real Layer 1 integration

#### 4. Sentiment Analysis

Correlates on-chain activity with social sentiment:

- Sentiment score: -1.0 (bearish) to +1.0 (bullish)
- Social mentions: Twitter, Discord, Reddit
- Correlation analysis: CONFIRMED, PARTIAL, DIVERGENT, UNCERTAIN

### Market Intelligence

#### 5. Token Tracking

- Real-time tracking of Qubic tokens (QX, QXALPHA, etc.)
- Risk scores per token
- 24h statistics and trends
- Liquidity and volume analysis

#### 6. Trading Signals

Automatic signal generation:

- **WHALE_DUMP_RISK**: Large sell orders detected
- **VOLUME_SPIKE**: Unusual volume increase
- **SUSPICIOUS_CLUSTER**: Coordinated activity patterns

### Predictive Analytics

#### 7. Risk Forecasting

- Per-wallet risk predictions
- Global network risk trends
- Exponential Moving Average (EMA) algorithms
- Confidence scoring

#### 8. Attack Simulation

Multiple scenario types:

- `whale_dump` - Large value transfers
- `wash_trade` - Circular trading patterns
- `flash_attack` - Rapid transaction bursts
- `wallet_drain` - Account draining patterns
- `spam_attack` - Network spam
- `liquidity_manipulation` - Pool manipulation

### Smart Contract Security

#### 9. SmartGuard Core Integration

**Strategic Integration**: In a previous Qubic Hackathon, we independently developed SmartGuard—an advanced C++ smart contract auditing platform that earned **2nd place** for its exceptional security analysis capabilities. When designing AEGIS, we recognized the perfect strategic alignment: SmartGuard protects contracts **before deployment**, while AEGIS protects them **during execution**. Rather than reinvent what already works, we made an intelligent decision: **integrate SmartGuard's proven expertise** into AEGIS's cognitive architecture.

This integration represents **strategic synergy**, not dependency. AEGIS operates independently as a complete security platform. SmartGuard Core enhances it by adding pre-deployment security—completing the full security lifecycle.

**SmartGuard Capabilities**:

- Static code analysis for C++ smart contracts
- Vulnerability detection (buffer overflows, infinite loops, logic errors)
- Automated documentation generation
- Functional specification creation
- Test plan generation
- Visual flow diagrams (Mermaid)
- Qubic-specific contract simulation

### Explainable AI (XAI)

#### 10. Transparent Decision Making

- AI-generated explanations for every risk assessment
- Structured risk factors
- Confidence levels
- Actionable recommendations

---

## Architecture

```
backend/
├── app/
│   ├── agents/                      # AI Agents
│   │   ├── agent_collector.py      # Transaction feature extraction
│   │   ├── agent_risk_analyst.py   # Real LLM-powered analysis
│   │   ├── agent_predictor.py      # EMA forecasting
│   │   ├── agent_simulator.py      # Attack scenarios
│   │   ├── agent_automator.py      # n8n integration
│   │   └── multi_agent_orchestrator.py  # Main coordinator
│   ├── core/
│   │   ├── ai_brain.py             # Groq integration
│   │   └── ai_brain_langchain.py   # LangChain alternative
│   ├── models/
│   │   ├── transaction.py          # Transaction model
│   │   ├── events.py               # RiskEvent model
│   │   └── market.py               # TokenStats, TokenSignal
│   ├── services/
│   │   ├── mock_generator.py       # Transaction generator
│   │   ├── qubic_simulation.py     # Realistic Qubic simulation
│   │   ├── qubic_data_replay.py    # Replay real data
│   │   ├── market_intel.py         # Market Intelligence service
│   │   ├── test_data_generator.py  # Test data generation
│   │   └── smart_guard/            # SmartGuard Core Integration
│   │       ├── service.py          # Main service wrapper
│   │       ├── graph/
│   │       │   └── graph_builder.py # LangGraph workflow
│   │       ├── nodes/
│   │       │   └── qubicdocs_nodes.py # Audit agents
│   │       ├── llms/
│   │       │   └── groqllm.py      # LLM configuration
│   │       ├── state/
│   │       │   └── state.py        # State management
│   │       └── utils/
│   │           └── validators.py   # Validation utilities
│   ├── api/
│   │   └── routes.py               # All API endpoints
│   └── config.py                   # Configuration
├── tests/
│   ├── test_automator_agent.py
│   ├── test_predector_agent.py
│   ├── test_risk_agent.py
│   ├── test_simulator_agent.py
│   ├── teste_collector_agent.py
│   └── verify_v2.py                # Market Intelligence tests
├── test_data/
│   ├── transactions.json
│   └── wallets.json
├── check_groq_setup.py             # Groq verification script
├── init_test_data.py               # Initialize test data
├── main.py                         # FastAPI app entry
├── requirements.txt
└── .env                            # Environment variables
```

---

## Quick Start

### Prerequisites

- **Python 3.9+** (recommended: 3.11+)
- **pip** package manager
- **Groq API key** (optional but strongly recommended for AI features)

### Installation

```bash
# 1. Navigate to backend directory
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
# Create .env file (see Configuration section)
cp .env.example .env  # Or create manually
# Edit .env and add your GROQ_API_KEY

# 4. Verify Groq setup (optional but recommended)
python check_groq_setup.py

# 5. Initialize test data (optional)
python init_test_data.py

# 6. Start the server
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

**API Documentation**:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# AI Configuration
GROQ_API_KEY=gsk_your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Options for GROQ_MODEL:
# - llama-3.3-70b-versatile (recommended, used by default)
# - llama-3.1-70b-versatile
# - mixtral-8x7b-32768

# Qubic Network
QUBIC_RPC_URL=https://api.qubic.org
QUBIC_REALISTIC_MODE=true

# n8n Integration (for active defense automation)
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
3. Go to "API Keys" section
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

**Note**: The system will work without Groq API key using rule-based analysis, but **real AI is strongly recommended** for best results.

---

## API Endpoints

### WebSocket

#### `WS /ws/monitor`

Real-time transaction monitoring stream. Clients receive continuous updates with transaction analysis, risk scores, DEFCON status, and more.

**Message Format**:

```json
{
  "type": "transaction_analysis",
  "data": {
    "transaction": {
      "id": "...",
      "from": "...",
      "to": "...",
      "amount": 1234.56,
      "token_symbol": "QXALPHA",
      "timestamp": "..."
    },
    "risk_score": 75.5,
    "risk_level": "HIGH",
    "explanation": "AI-generated explanation...",
    "prediction": {
      "future_risk": 80.0,
      "confidence": 0.85,
      "horizon": "short_term"
    },
    "defcon_status": {
      "defcon_level": 3,
      "alert_threshold": 70.0,
      "attacks_last_minute": 3
    },
    "sentiment_analysis": {
      "sentiment_label": "BEARISH",
      "sentiment_score": -0.65,
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

#### Market Intelligence

- **`GET /api/market-intel/overview`** - Combined tokens overview and signals
- **`GET /api/tokens`** - All tracked tokens with stats
- **`GET /api/tokens/{symbol}`** - Specific token details (e.g., `/api/tokens/QXALPHA`)
- **`GET /api/signals`** - Recent trading/security signals
- **`GET /api/network-emotion`** - Network-wide sentiment analysis

#### Predictions & Forecasting

- **`GET /api/predict`** - Risk predictions
  - Query params:
    - `horizon` (optional): `short_term`, `medium_term`, `long_term`
    - `wallet_id` (optional): Specific wallet analysis

#### Attack Simulation

- **`POST /api/simulate`** - Simulate attack scenario
  - Body:
    ```json
    {
      "scenario_type": "whale_dump",
      "parameters": {
        "amount": 50000,
        "wallet_id": "..."
      }
    }
    ```
  - Scenarios: `whale_dump`, `wash_trade`, `flash_attack`, `wallet_drain`, `spam_attack`, `liquidity_manipulation`

#### Wallet Analysis

- **`GET /api/wallet-graph`** - Wallet interaction graph
  - Query params:
    - `max_nodes` (optional, default: 50): Maximum nodes in graph
- **`GET /api/wallet/{wallet_id}`** - Specific wallet analysis

#### AI Chat

- **`POST /api/ask-aegis`** - Chat with AI security copilot
  - Body:
    ```json
    {
      "message": "Your question about Qubic security",
      "context": {
        "wallet_id": "...",
        "transaction_id": "..."
      }
    }
    ```

#### Automation

- **`POST /api/trigger-automation`** - Trigger n8n webhook
  - Body:
    ```json
    {
      "scenario_type": "WHALE",
      "message": "Custom message"
    }
    ```
- **`POST /api/trigger-automation-riskevent`** - Trigger with RiskEvent model
  - Body:
    ```json
    {
      "risk_event": {
        "risk_score": 95,
        "risk_level": "CRITICAL",
        "explanation": "..."
      },
      "webhook_url": "..."
    }
    ```

#### Smart Contract Auditing (SmartGuard)

- **`POST /api/smart-guard/audit`** - Complete SmartGuard audit pipeline (8 steps)

  - Body:
    ```json
    {
      "code": "#include <iostream>\n...",
      "language": "english"
    }
    ```
  - Returns: Full audit report with comments, security analysis, documentation, flow diagrams, tests, and recommendations

- **`POST /api/smart-guard/quick-audit`** - Quick security audit (semantic analysis + security audit only)
  - Body:
    ```json
    {
      "code": "#include <iostream>\n...",
      "language": "english"
    }
    ```
  - Returns: Quick security assessment without full documentation

**Note**: SmartGuard endpoints require LangGraph dependencies. If not available, endpoints return 503 status with helpful error message.

---

## AI Features

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

## SmartGuard Core Integration

### Overview

SmartGuard Core is integrated as a strategic enhancement to AEGIS, providing pre-deployment security analysis for C++ smart contracts. It uses LangGraph to orchestrate an 8-step auditing pipeline:

1. **Code Explanation & Commenting** - AI explains code functionality
2. **Comment Review** - Validates and improves comments
3. **Semantic Analysis** - Deep code understanding
4. **Security Audit** - Vulnerability detection
5. **Strict Validation** - Compliance checking
6. **Specification Generation** - Functional specifications
7. **Flow Diagram** - Visual representation (Mermaid)
8. **Test Generation** - Automated test plans

### Usage

**Full Audit**:

```python
POST /api/smart-guard/audit
{
  "code": "#include <iostream>\n...",
  "language": "english"
}
```

**Quick Audit**:

```python
POST /api/smart-guard/quick-audit
{
  "code": "#include <iostream>\n...",
  "language": "english"
}
```

### Dependencies

SmartGuard requires:

- `langgraph>=0.1.0`
- `langchain>=0.2.0`
- `langchain-groq>=0.1.0`
- `groq>=0.10.0`

If these are not installed, AEGIS continues to function normally, but SmartGuard endpoints will return 503.

---

## Testing

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

### Testing SmartGuard

```bash
# Test SmartGuard audit
curl -X POST http://localhost:8000/api/smart-guard/audit \
  -H "Content-Type: application/json" \
  -d '{
    "code": "#include <iostream>\nint main() { return 0; }",
    "language": "english"
  }'
```

---

## Development

### Project Structure

- **Agents**: Modular AI agents for different tasks
- **Core**: Core AI brain and intelligence engine
- **Models**: Pydantic models for type safety
- **Services**: Business logic (mock generation, market intel, SmartGuard)
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

## Deployment

### Production Considerations

1. **Environment Variables**: Use secure secret management
2. **CORS**: Restrict origins in production
3. **Rate Limiting**: Add rate limiting for API endpoints
4. **Monitoring**: Add logging and monitoring
5. **Database**: Consider persistent storage for production
6. **WebSocket**: Configure proper WebSocket proxy (nginx, etc.)

### Docker (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Nginx Configuration (WebSocket)

```nginx
location /ws/ {
    proxy_pass http://backend:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

---

## Troubleshooting

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

### SmartGuard Not Available

If SmartGuard endpoints return 503:

1. Check if LangGraph dependencies are installed:
   ```bash
   pip install langgraph langchain langchain-groq
   ```
2. Verify Groq API key is configured
3. Check backend logs for detailed error messages

---

## Performance

### Optimization Tips

- **Groq API**: Fast inference (~200ms per request)
- **Caching**: Consider caching frequent queries
- **WebSocket**: Efficient real-time streaming
- **Lazy Loading**: SmartGuard uses lazy loading to avoid startup delays

### Monitoring

Monitor these metrics:

- API response times
- WebSocket connection count
- Groq API usage and rate limits
- Memory usage (especially for graph operations)

---

## Security

### Best Practices

1. **API Keys**: Never commit `.env` files
2. **CORS**: Restrict in production
3. **Rate Limiting**: Implement for all endpoints
4. **Input Validation**: All inputs validated via Pydantic
5. **Error Handling**: No sensitive data in error messages

---

## Version History

### v2.1 (Current)

- ✅ Market Intelligence (V2) - Token tracking and signals
- ✅ DEFCON Mode - Adaptive thresholds
- ✅ Active Defense - Simulated firewall blocks
- ✅ Sentiment Analysis - Social correlation
- ✅ Enhanced AI prompts - More context and intelligence
- ✅ Improved error handling - Robust Groq integration
- ✅ SmartGuard Core Integration - Pre-deployment contract auditing
- ✅ Production-ready code cleanup

### v2.0

- Multi-agent system
- Real AI analysis (Groq)
- Predictive analytics
- Attack simulation
- WebSocket streaming

---

## Contributing

This is a hackathon project, but contributions welcome!

---

## License

MIT License - Hackathon Project

---

## Acknowledgments

- **Groq** for ultra-fast AI inference
- **Qubic** for the amazing blockchain
- **FastAPI** for the excellent framework
- **LangGraph** for multi-agent orchestration
- **LangChain** for LLM integration

---

**Built for the Qubic Hackathon**
