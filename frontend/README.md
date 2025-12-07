# QUBIC AEGIS Frontend

**Version 2.1** - React + TypeScript + Tailwind CSS Dashboard

---

## Overview

Modern, real-time dashboard for **QUBIC AEGIS** - Predictive AI Multi-Agent Security & Risk Intelligence System. Built with React, TypeScript, Vite, and Tailwind CSS with a cyberpunk-inspired design theme.

The frontend provides an intuitive interface for monitoring Qubic blockchain transactions, analyzing risks, viewing market intelligence, auditing smart contracts, and interacting with the AI security copilot.

---

## Tech Stack

- **React 19** - Modern UI framework
- **TypeScript 5.9** - Type safety and developer experience
- **Vite 7** - Lightning-fast build tool and dev server
- **Tailwind CSS 3.4** - Utility-first CSS framework
- **React Router DOM 6** - Client-side routing
- **Recharts 3.5** - Data visualization library
- **react-force-graph-2d** - Interactive graph visualization
- **Sonner** - Toast notifications
- **Lucide React** - Icon library
- **Framer Motion** - Smooth animations

---

## Features

### Core Pages

#### 1. **Live Monitor** (`/`)

Real-time transaction monitoring dashboard with comprehensive risk analysis.

**Features**:
- Real-time risk monitoring with live updates
- Risk gauge with visual indicator (0-100 scale)
- Live transaction feed with token information
- Agent thoughts log stream (AI reasoning)
- Risk history chart with AI predictions
- DEFCON status widget with adaptive thresholds
- Network statistics (transactions, wallets, tokens)
- Trigger automation button for active defense
- Alert animations (gentle pulse effect, only on this page)

**Components**:
- `RiskGauge` - Circular risk score indicator
- `TransactionFeed` - Live transaction stream with token symbols
- `AgentThoughts` - Scrolling log terminal
- `RiskChart` - Historical risk with AI predictions
- `DEFCONWidget` - DEFCON status indicator
- `NetworkStats` - Network statistics

#### 2. **Market Intelligence** (`/market-intel`)

Comprehensive token tracking and trading signals.

**Features**:
- Token tracking overview (QX, QXALPHA, CFB, etc.)
- Advanced filtering and search
- Sorting capabilities (Risk, Alerts, Trend)
- Live signals terminal
- Real-time updates (2s refresh interval)
- Token statistics (24h alerts, average risk, trends)
- Risk labels and liquidity tags

**Components**:
- Token list with filtering
- Signals terminal
- Real-time data refresh

#### 3. **Wallet Graph** (`/graph`)

Interactive visualization of wallet interactions and network topology.

**Features**:
- Interactive force-directed graph
- Wallet interaction visualization
- Cluster analysis
- Node filtering and zoom controls
- Detailed wallet information on click
- Node size based on transaction volume
- Color coding by risk level

**Components**:
- `WalletGraph` - 2D force-directed graph
- `WalletGraphEnterprise` - Enhanced graph visualization

#### 4. **Predictions** (`/predictions`)

Risk forecasting and trend analysis.

**Features**:
- Global risk predictions
- Per-wallet forecasting
- Trend analysis (UP/DOWN/STABLE)
- Confidence scoring
- Historical and predicted risk charts
- Multiple time horizons (short/medium/long term)

**Components**:
- Prediction cards
- Risk trend charts
- Confidence indicators

#### 5. **Attack Simulator** (`/simulator` or `/war-room`)

Simulate attack scenarios and analyze potential impacts.

**Features**:
- Multiple attack scenario simulation
- Step-by-step breakdown
- AI-generated recommendations
- Impact estimation
- Peak risk calculation
- Scenario types: whale_dump, wash_trade, flash_attack, wallet_drain, spam_attack, liquidity_manipulation

**Components**:
- Scenario selector
- Attack visualization
- Impact analysis

#### 6. **SmartGuard** (`/smart-guard`)

Smart contract auditing interface with integrated SmartGuard Core.

**Features**:
- Code editor for C++ smart contracts
- Full audit pipeline (8-step analysis)
- Quick audit option (semantic + security only)
- Rich markdown result display
- Interactive Mermaid flow diagrams
- Full-screen results view
- Collapsible code editor when results are shown
- Comprehensive audit reports with:
  - Code comments and explanations
  - Security vulnerability analysis
  - Functional specifications
  - Test plans
  - Visual flow diagrams
  - Recommendations

**Components**:
- Code editor
- `MarkdownRenderer` - Custom markdown display
- `MermaidDiagram` - Interactive diagram rendering

**SmartGuard Integration**: Uses the integrated SmartGuard Core from backend (2nd-place hackathon winner) for pre-deployment contract security analysis.

#### 7. **AI Chat** (`/chat`)

Interactive chat interface with AI security copilot.

**Features**:
- AI-powered chat interface
- Real-time responses from backend
- Context-aware conversations
- Wallet graph visualization alongside chat
- Message history
- Typing indicators

**Components**:
- Chat interface
- Message bubbles
- Graph visualization

#### 8. **Dashboard** (`/dashboard`)

Alternative dashboard view with different layout and emphasis.

---

### Key Components

#### UI Components (`src/components/ui/`)

Reusable UI components built with Tailwind CSS:
- `Button` - Styled buttons with variants
- `Card` - Card container component
- `Input` - Form input fields
- `Badge` - Status badges
- `Select` - Dropdown selects
- `ScrollArea` - Scrollable containers

#### Specialized Components

- **`RiskGauge`** - Circular risk score indicator (0-100)
- **`TransactionFeed`** - Live transaction stream with token symbols
- **`AgentThoughts`** - Scrolling log terminal for AI reasoning
- **`RiskChart`** - Historical risk with AI predictions (Recharts)
- **`DEFCONWidget`** - DEFCON status indicator with level badges
- **`WalletGraph`** / **`WalletGraphEnterprise`** - Interactive graph visualizations
- **`Header`** - Global header with DEFCON status and connection indicator
- **`Sidebar`** - Navigation sidebar with page links
- **`NetworkStats`** - Network statistics display
- **`MarkdownRenderer`** - Custom markdown renderer with cyberpunk styling
- **`MermaidDiagram`** - Mermaid diagram renderer with cyberpunk theme
- **`ActionNotification`** - Toast notifications for actions

---

## Installation

### Prerequisites

- **Node.js 18+** (recommended: 20+)
- **npm** or **yarn** package manager

### Setup

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Configure environment (optional)
# Create .env file (see Configuration section)

# 4. Start development server
npm run dev
```

The application will be available at `http://localhost:5173`

### Build for Production

```bash
# Build optimized production bundle
npm run build

# Preview production build locally
npm run preview
```

Production build outputs to `dist/` directory.

---

## Configuration

### Environment Variables

Create a `.env` file in the `frontend/` directory (optional):

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

**Default values**:
- `VITE_API_URL`: `http://localhost:8000` (backend API)
- `VITE_WS_URL`: `ws://localhost:8000` (WebSocket endpoint)

These defaults assume backend is running on `http://localhost:8000`.

---

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/                      # Reusable UI components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── select.tsx
│   │   │   └── scroll-area.tsx
│   │   ├── action-notification.tsx  # Toast notifications
│   │   ├── agent-thoughts.tsx       # AI reasoning log
│   │   ├── analysis-modal.tsx       # Analysis modal
│   │   ├── defcon-badge.tsx         # DEFCON level badge
│   │   ├── defcon-widget.tsx        # DEFCON status widget
│   │   ├── header.tsx               # Global header
│   │   ├── markdown-renderer.tsx    # Markdown display
│   │   ├── mermaid-diagram.tsx      # Mermaid diagrams
│   │   ├── network-stats.tsx        # Network statistics
│   │   ├── risk-chart.tsx           # Risk visualization
│   │   ├── risk-gauge.tsx           # Risk gauge indicator
│   │   ├── sentiment-gauge.tsx      # Sentiment indicator
│   │   ├── sidebar.tsx              # Navigation sidebar
│   │   ├── simulation-card.tsx      # Attack simulation card
│   │   ├── transaction-feed.tsx     # Transaction stream
│   │   ├── wallet-graph.tsx         # Basic wallet graph
│   │   └── wallet-graph-enterprise.tsx  # Enhanced graph
│   ├── contexts/
│   │   └── ConnectionContext.tsx    # WebSocket connection state
│   ├── pages/
│   │   ├── Chat.tsx                 # AI chat interface
│   │   ├── Dashboard.tsx            # Alternative dashboard
│   │   ├── Graph.tsx                # Wallet graph page
│   │   ├── LiveMonitor.tsx          # Live monitor (home)
│   │   ├── NeuralSearch.tsx         # Search page
│   │   ├── Predictions.tsx          # Risk predictions
│   │   ├── Simulator.tsx            # Attack simulator
│   │   ├── SmartGuard.tsx           # Smart contract auditing
│   │   ├── TokenIntel.tsx           # Market intelligence
│   │   └── WarRoom.tsx              # War room (simulator alt)
│   ├── lib/
│   │   └── utils.ts                 # Utility functions (clsx, etc.)
│   ├── App.tsx                      # Main app component with routing
│   ├── App.css                      # App-specific styles
│   ├── main.tsx                     # Entry point
│   └── index.css                    # Global styles
├── public/
│   └── vite.svg                     # Vite logo
├── index.html                       # HTML template
├── package.json                     # Dependencies
├── package-lock.json                # Lock file
├── tailwind.config.js               # Tailwind configuration
├── postcss.config.js                # PostCSS configuration
├── tsconfig.json                    # TypeScript config
├── tsconfig.app.json                # TypeScript app config
├── tsconfig.node.json               # TypeScript node config
├── vite.config.ts                   # Vite configuration
└── eslint.config.js                 # ESLint configuration
```

---

## WebSocket Integration

The frontend connects to the backend WebSocket at `ws://localhost:8000/ws/monitor` for real-time data streaming.

### Connection Management

- Automatic reconnection on disconnect
- Connection status indicator in header ("ONLINE" / "OFFLINE")
- Connection context shared across components via `ConnectionContext`
- Graceful error handling

### Message Handling

Messages received via WebSocket:

```typescript
{
  type: "transaction_analysis",
  data: {
    transaction: {
      id: string,
      from: string,
      to: string,
      amount: number,
      token_symbol?: string,
      timestamp: string
    },
    risk_score: number,
    risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
    explanation: string,
    prediction: {
      future_risk: number,
      confidence: number,
      horizon: "short_term" | "medium_term" | "long_term"
    },
    defcon_status: {
      defcon_level: 1 | 2 | 3 | 4 | 5,
      alert_threshold: number,
      attacks_last_minute: number
    },
    sentiment_analysis: {
      sentiment_label: string,
      sentiment_score: number,
      correlation_with_risk: string
    },
    active_defense?: {
      action: string,
      status: string
    }
  }
}
```

### Usage Example

```typescript
import { useContext } from 'react';
import { ConnectionContext } from '@/contexts/ConnectionContext';

function MyComponent() {
  const { isConnected, lastMessage } = useContext(ConnectionContext);
  
  // Use connection status and messages
}
```

---

## API Integration

### REST Endpoints Used

- **Health & Status**:
  - `GET /api/health` - Health check
  - `GET /api/defcon-status` - DEFCON level and status

- **Market Intelligence**:
  - `GET /api/market-intel/overview` - Combined tokens overview and signals
  - `GET /api/tokens` - All tracked tokens
  - `GET /api/tokens/{symbol}` - Specific token details
  - `GET /api/signals` - Trading/security signals
  - `GET /api/network-emotion` - Network-wide sentiment

- **Predictions**:
  - `GET /api/predict` - Risk predictions (with optional `horizon` and `wallet_id` params)

- **Wallet Analysis**:
  - `GET /api/wallet-graph` - Wallet graph data (with optional `max_nodes` param)
  - `GET /api/wallet/{wallet_id}` - Specific wallet analysis

- **Attack Simulation**:
  - `POST /api/simulate` - Simulate attack scenario

- **AI Chat**:
  - `POST /api/ask-aegis` - Chat with AI security copilot

- **Automation**:
  - `POST /api/trigger-automation` - Trigger n8n automation

- **Smart Contract Auditing**:
  - `POST /api/smart-guard/audit` - Full SmartGuard audit
  - `POST /api/smart-guard/quick-audit` - Quick security audit

### API Client

API calls are made using native `fetch`. Configuration:

```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Example API call
const response = await fetch(`${API_URL}/api/health`);
const data = await response.json();
```

---

## Styling

### Design System

**Color Palette** (Cyberpunk Theme):
- Background: `#0a0a0a` (near-black)
- Primary: `#00ff88` (neon green)
- Secondary: `#1a1a1a` (dark gray)
- Accent: `#0066ff` (neon blue)
- Destructive: `#ff3250` (red)
- Warning: `#ffaa00` (orange)
- Muted: Various shades for text and borders

**Typography**:
- Primary: Monospace font family (`'Courier New', monospace`)
- Headings: Bold, uppercase, tight tracking
- Body: Regular weight, readable sizes (14px-16px)

**Components**:
- Cards with subtle borders (`border border-gray-800`)
- Cyberpunk-inspired glows and animations
- Smooth transitions (200-300ms)
- Loading states with spinners
- Hover effects with subtle glow

**Animations**:
- `gentle-pulse` - Soft pulsing animation for alerts (used on Live Monitor page only)
- `pulse` - Standard pulse animation
- `fade-in` - Fade-in transitions
- Smooth scroll behavior

### Tailwind Configuration

Custom theme extends default Tailwind with:
- Custom colors matching cyberpunk theme
- Custom animations (pulse, glow effects)
- Monospace font stack
- Extended spacing scale

See `tailwind.config.js` for full configuration.

---

## State Management

### React Context API

**ConnectionContext** (`src/contexts/ConnectionContext.tsx`):
- Manages WebSocket connection state
- Provides connection status (`isConnected`)
- Provides last received message (`lastMessage`)
- Handles reconnection logic

### Local State

- **useState** - Component-level state management
- **useEffect** - Side effects and data fetching
- **useCallback** - Memoized callbacks for performance
- **useMemo** - Memoized computed values

---

## Performance Optimizations

- **React.memo** - Memoization for expensive components
- **useCallback** - Memoized event handlers to prevent unnecessary re-renders
- **Debounced API calls** - Prevents excessive API requests
- **Virtual scrolling** - Via ScrollArea component for large lists
- **Lazy loading** - Graph visualizations loaded on demand
- **Code splitting** - Automatic via Vite
- **Optimized re-renders** - Careful dependency management

---

## Error Handling

- **Error Boundaries** - `ErrorBoundary` component catches React errors
- **API Error Handling** - Try-catch blocks with user-friendly error messages
- **WebSocket Errors** - Automatic reconnection with exponential backoff
- **Fallback UI** - Loading states and error messages
- **Toast Notifications** - User feedback via Sonner

---

## Browser Support

- **Chrome/Edge** (latest) ✅
- **Firefox** (latest) ✅
- **Safari** (latest) ✅

Requires modern browser with:
- WebSocket support
- ES6+ JavaScript support
- CSS Grid and Flexbox support

---

## Development

### Running in Development

```bash
npm run dev
```

Starts Vite dev server with:
- Hot Module Replacement (HMR)
- Fast refresh
- Source maps
- Type checking

### Building for Production

```bash
npm run build
```

Outputs optimized production build to `dist/` directory:
- Minified JavaScript
- Optimized CSS
- Tree-shaking
- Code splitting

### Type Checking

```typescript
// TypeScript checks are run during build
// For IDE support, ensure tsconfig.json is properly configured
```

### Linting

```bash
npm run lint
```

Uses ESLint with:
- React hooks rules
- TypeScript rules
- Modern JavaScript rules

---

## Testing

### Manual Testing Checklist

- [ ] WebSocket connection establishes on page load
- [ ] All pages load without errors
- [ ] Real-time updates work correctly
- [ ] Navigation between pages works smoothly
- [ ] All API calls succeed
- [ ] Error states display properly
- [ ] Loading states show appropriately
- [ ] Alert animations work (only on Live Monitor page)
- [ ] SmartGuard audit displays results correctly
- [ ] Mermaid diagrams render properly
- [ ] Markdown formatting is correct
- [ ] Responsive design works on different screen sizes

---

## Troubleshooting

### WebSocket Connection Issues

**Problem**: Connection status shows "OFFLINE"

**Solutions**:
1. Verify backend is running on port 8000
2. Check browser console for connection errors
3. Ensure CORS is configured correctly on backend
4. Check firewall settings
5. Verify WebSocket endpoint: `ws://localhost:8000/ws/monitor`

### API Call Failures

**Problem**: API requests fail with network errors

**Solutions**:
1. Verify backend API is accessible: `curl http://localhost:8000/api/health`
2. Check network tab in browser dev tools
3. Verify endpoint URLs are correct
4. Check CORS configuration on backend
5. Verify environment variables are set correctly

### Build Issues

**Problem**: Build fails or errors occur

**Solutions**:
1. Clear `node_modules` and reinstall:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```
2. Clear Vite cache:
   ```bash
   rm -rf node_modules/.vite
   ```
3. Check Node.js version compatibility (requires 18+)
4. Verify all dependencies are installed correctly

### SmartGuard Not Displaying Results

**Problem**: Audit results don't display or format incorrectly

**Solutions**:
1. Check browser console for errors
2. Verify backend SmartGuard endpoint is working
3. Check that markdown rendering is working
4. Verify Mermaid.js is loading correctly
5. Check network tab for failed requests

### Styling Issues

**Problem**: Styles not applying or looking incorrect

**Solutions**:
1. Verify Tailwind is compiling correctly
2. Check that classes are not being purged incorrectly
3. Restart dev server
4. Clear browser cache
5. Check `tailwind.config.js` configuration

---

## Future Enhancements

- [ ] Unit and integration tests (Jest, React Testing Library)
- [ ] E2E testing (Playwright/Cypress)
- [ ] PWA capabilities (service worker, offline support)
- [ ] Dark/light theme toggle
- [ ] Internationalization (i18n) support
- [ ] Performance monitoring (Web Vitals)
- [ ] Error tracking (Sentry integration)
- [ ] Advanced filtering and search
- [ ] Export functionality (PDF reports, CSV data)
- [ ] Customizable dashboard layouts

---

## Deployment

### Production Build

```bash
npm run build
```

### Static Hosting

The frontend is a static SPA and can be deployed to:
- **Vercel** - Recommended for easy deployment
- **Netlify** - Simple static hosting
- **GitHub Pages** - Free hosting
- **AWS S3 + CloudFront** - Scalable hosting
- **Any static hosting service**

### Environment Variables in Production

Set environment variables in your hosting platform:
- `VITE_API_URL` - Backend API URL
- `VITE_WS_URL` - WebSocket URL (use `wss://` for secure WebSocket)

### Nginx Configuration (if self-hosting)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/qubic-aegis-frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

---

## License

MIT License - Hackathon Project

---

## Acknowledgments

- **React** team for the amazing framework
- **Vite** for the lightning-fast build tool
- **Tailwind CSS** for the utility-first CSS
- **Recharts** for data visualization
- **react-force-graph** for graph visualizations
- **Mermaid.js** for diagram rendering

---

**Built with React, TypeScript, and Tailwind CSS for the Qubic Hackathon**
