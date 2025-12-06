# QUBIC AEGIS Frontend

**Version 2.1** - React + TypeScript + Tailwind CSS Dashboard

## Overview

Modern, real-time dashboard for QUBIC AEGIS - Predictive AI Multi-Agent Security & Risk Intelligence System. Built with React, TypeScript, Vite, and Tailwind CSS with a cyberpunk-inspired design theme.

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS
- **React Router DOM** - Client-side routing
- **Recharts** - Data visualization
- **react-force-graph-2d** - Interactive graph visualization
- **Sonner** - Toast notifications
- **Lucide React** - Icon library

## Features

### Core Pages

1. **Dashboard** (`/`)

   - Real-time risk monitoring
   - Risk gauge with visual indicator
   - Live transaction feed with token information
   - Agent thoughts log stream
   - Risk history chart with AI predictions
   - DEFCON status widget
   - Network statistics
   - Trigger automation button

2. **Market Intelligence** (`/market-intel`)

   - Token tracking overview (QX, QXALPHA, etc.)
   - Advanced filtering and search
   - Sorting capabilities (Risk, Alerts, Trend)
   - Live signals terminal
   - Real-time updates (2s refresh interval)

3. **Wallet Graph** (`/graph`)

   - Interactive 3D force-directed graph
   - Wallet interaction visualization
   - Cluster analysis
   - Node filtering and zoom controls
   - Detailed wallet information on click

4. **Predictions** (`/predictions`)

   - Global risk predictions
   - Per-wallet forecasting
   - Trend analysis (UP/DOWN/STABLE)
   - Confidence scoring
   - Historical and predicted risk charts

5. **Attack Simulator** (`/simulator`)

   - Multiple attack scenario simulation
   - Step-by-step breakdown
   - AI-generated recommendations
   - Impact estimation
   - Peak risk calculation

6. **Ask Aegis** (`/chat`)
   - AI-powered chat interface
   - Real-time responses from backend
   - Context-aware conversations
   - Wallet graph visualization alongside chat

### Key Components

- **RiskGauge** - Circular risk score indicator
- **TransactionFeed** - Live transaction stream with token symbols
- **AgentThoughts** - Scrolling log terminal
- **RiskChart** - Historical risk with AI predictions
- **DEFCONWidget** - DEFCON status indicator
- **WalletGraph** / **WalletGraphEnterprise** - Interactive graph visualizations
- **Header** - Global header with DEFCON status and connection indicator
- **Sidebar** - Navigation sidebar

## Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Configuration

### Environment Variables

Create a `.env` file in the `frontend/` directory (optional):

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

Default values assume backend is running on `http://localhost:8000`.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # Reusable UI components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   └── ...
│   │   ├── agent-thoughts.tsx
│   │   ├── defcon-widget.tsx
│   │   ├── header.tsx
│   │   ├── network-stats.tsx
│   │   ├── risk-chart.tsx
│   │   ├── risk-gauge.tsx
│   │   ├── transaction-feed.tsx
│   │   ├── wallet-graph.tsx
│   │   └── wallet-graph-enterprise.tsx
│   ├── contexts/
│   │   └── ConnectionContext.tsx  # WebSocket connection state
│   ├── pages/
│   │   ├── Chat.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Graph.tsx
│   │   ├── Predictions.tsx
│   │   ├── Simulator.tsx
│   │   └── TokenIntel.tsx
│   ├── lib/
│   │   └── utils.ts          # Utility functions
│   ├── App.tsx               # Main app component with routing
│   ├── main.tsx              # Entry point
│   └── index.css             # Global styles
├── public/
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

## WebSocket Integration

The frontend connects to the backend WebSocket at `ws://localhost:8000/ws/monitor` for real-time data streaming.

### Connection Management

- Automatic reconnection on disconnect
- Connection status indicator in header
- Connection context shared across components

### Message Handling

Messages received via WebSocket:

```typescript
{
  type: "transaction_analysis",
  data: {
    transaction: {...},
    risk_score: number,
    risk_level: string,
    defcon_status: {...},
    sentiment_analysis: {...},
    active_defense: {...},
    // ...
  }
}
```

## API Integration

### REST Endpoints Used

- `GET /api/health` - Health check
- `GET /api/defcon-status` - DEFCON level and status
- `GET /api/market-intel/overview` - Market intelligence data
- `GET /api/tokens` - All tracked tokens
- `GET /api/tokens/{symbol}` - Specific token details
- `GET /api/signals` - Trading/security signals
- `GET /api/predict` - Risk predictions
- `GET /api/wallet-graph` - Wallet graph data
- `POST /api/simulate` - Attack simulation
- `POST /api/ask-aegis` - AI chat
- `POST /api/trigger-automation` - Trigger n8n automation

## Styling

### Design System

**Color Palette:**

- Background: `#0a0a0a` (near-black)
- Primary: `#00ff88` (neon green)
- Secondary: `#1a1a1a` (dark gray)
- Destructive: `#ff3250` (red)
- Muted: Various shades for text and borders

**Typography:**

- Primary: Monospace font family
- Headings: Bold, uppercase, tracking-tight
- Body: Regular weight, readable sizes

**Components:**

- Cards with subtle borders and hover effects
- Cyberpunk-inspired glows and animations
- Smooth transitions and loading states

### Tailwind Configuration

Custom theme extends default Tailwind with:

- Custom colors matching cyberpunk theme
- Custom animations (pulse, glow effects)
- Monospace font stack

## State Management

- **React Context API** - WebSocket connection state
- **Local State (useState)** - Component-level state
- **Effects (useEffect)** - Side effects and data fetching

## Performance Optimizations

- React.memo for expensive components
- useCallback for event handlers
- Debounced API calls where appropriate
- Virtual scrolling for large lists (via ScrollArea)
- Lazy loading for graph visualizations

## Error Handling

- Graceful fallbacks for API failures
- Error boundaries for component crashes
- User-friendly error messages
- Retry logic for failed requests

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

Requires modern browser with WebSocket and ES6+ support.

## Development

### Running in Development

```bash
npm run dev
```

Starts Vite dev server with hot module replacement.

### Building for Production

```bash
npm run build
```

Outputs optimized production build to `dist/` directory.

### Type Checking

```bash
npm run type-check
```

### Linting

```bash
npm run lint
```

## Testing

Manual testing checklist:

- [ ] WebSocket connection establishes
- [ ] All pages load without errors
- [ ] Real-time updates work correctly
- [ ] Navigation between pages works
- [ ] All API calls succeed
- [ ] Error states display properly
- [ ] Loading states show appropriately

## Troubleshooting

### WebSocket Connection Issues

- Verify backend is running on port 8000
- Check browser console for connection errors
- Ensure CORS is configured correctly on backend

### API Call Failures

- Verify backend API is accessible
- Check network tab in browser dev tools
- Verify endpoint URLs are correct

### Build Issues

- Clear `node_modules` and reinstall
- Clear Vite cache: `rm -rf node_modules/.vite`
- Check Node.js version compatibility

## Future Enhancements

- Unit and integration tests
- E2E testing with Playwright/Cypress
- PWA capabilities
- Dark/light theme toggle
- Internationalization (i18n)
- Performance monitoring
- Error tracking (Sentry)

## License

MIT License - Hackathon Project

---

Built with React, TypeScript, and Tailwind CSS for the Qubic Hackathon.
