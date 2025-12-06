"""
Market Intelligence Service
Manages token-level intelligence and trading signals
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import deque, defaultdict
from app.models.market import TokenStats, TokenSignal


class MarketIntelService:
    """
    Manages token-level intelligence:
    - token stats (aggregated risk, alerts, trend)
    - token signals (whale risk, suspicious patterns)
    Uses in-memory storage (fine for hackathon).
    """
    
    def __init__(self, max_signals: int = 200):
        self.token_stats: Dict[str, TokenStats] = {}
        self.token_signals: deque[TokenSignal] = deque(maxlen=max_signals)
        
        # Maintain per-token risk history for trend calculation
        # Format: {token_symbol: deque[(timestamp, risk_score)]}
        self.token_risk_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Token metadata cache (can be extended)
        self.token_metadata: Dict[str, Dict[str, str]] = {}
    
    def update_token_from_event(
        self,
        token_symbol: str,
        risk_score: float,
        risk_level: str,
        xai_summary: str | None = None
    ) -> TokenStats:
        """
        Update internal stats for a token based on a new risk event.
        
        Args:
            token_symbol: Token symbol (e.g. "QX", "QXALPHA")
            risk_score: Risk score (0-100)
            risk_level: Risk level ("LOW", "MEDIUM", "HIGH", "CRITICAL")
            xai_summary: Optional AI explanation
        
        Returns:
            Updated TokenStats
        """
        now = datetime.utcnow()
        
        # Add to history
        self.token_risk_history[token_symbol].append((now, risk_score))
        
        # Get or create token stats
        if token_symbol not in self.token_stats:
            # Initialize new token
            self.token_stats[token_symbol] = TokenStats(
                symbol=token_symbol,
                name=self.token_metadata.get(token_symbol, {}).get("name"),
                last_updated=now,
                latest_risk_score=risk_score,
                average_risk_24h=risk_score,
                alerts_24h=0,
                trend="STABLE",
                liquidity_tag=self._infer_liquidity_tag(token_symbol),
                risk_label=self._compute_risk_label(risk_score)
            )
        else:
            # Update existing token
            token_stat = self.token_stats[token_symbol]
            token_stat.last_updated = now
            token_stat.latest_risk_score = risk_score
        
        # Update alerts count (increment if HIGH/CRITICAL)
        if risk_level in ("HIGH", "CRITICAL"):
            # Count alerts in last 24h
            cutoff = now - timedelta(hours=24)
            recent_alerts = sum(
                1 for ts in self.token_risk_history[token_symbol]
                if ts[0] >= cutoff and ts[1] >= 70
            )
            self.token_stats[token_symbol].alerts_24h = recent_alerts
        
        # Recompute average_risk_24h
        cutoff = now - timedelta(hours=24)
        recent_risks = [
            risk for ts, risk in self.token_risk_history[token_symbol]
            if ts >= cutoff
        ]
        if recent_risks:
            self.token_stats[token_symbol].average_risk_24h = sum(recent_risks) / len(recent_risks)
        else:
            self.token_stats[token_symbol].average_risk_24h = risk_score
        
        # Compute trend (UP/DOWN/STABLE)
        trend = self._compute_trend(token_symbol)
        self.token_stats[token_symbol].trend = trend
        
        # Update risk label
        self.token_stats[token_symbol].risk_label = self._compute_risk_label(risk_score)
        
        return self.token_stats[token_symbol]
    
    def _compute_trend(self, token_symbol: str) -> str:
        """Compute trend (UP/DOWN/STABLE) based on recent risk history"""
        history = list(self.token_risk_history[token_symbol])
        if len(history) < 5:
            return "STABLE"
        
        # Compare last 5 vs previous 5
        recent_5 = history[-5:]
        previous_5 = history[-10:-5] if len(history) >= 10 else history[:5]
        
        if len(previous_5) == 0:
            return "STABLE"
        
        recent_avg = sum(r for _, r in recent_5) / len(recent_5)
        previous_avg = sum(r for _, r in previous_5) / len(previous_5)
        
        diff = recent_avg - previous_avg
        
        if diff > 10:
            return "UP"
        elif diff < -10:
            return "DOWN"
        else:
            return "STABLE"
    
    def _compute_risk_label(self, risk_score: float) -> str:
        """Compute human-readable risk label"""
        if risk_score < 30:
            return "SAFE"
        elif risk_score < 50:
            return "LOW_RISK"
        elif risk_score < 70:
            return "WATCHLIST"
        elif risk_score < 90:
            return "HIGH_RISK"
        else:
            return "CRITICAL"
    
    def _infer_liquidity_tag(self, token_symbol: str) -> str:
        """Infer liquidity tag (simple heuristic)"""
        # Common tokens might have higher liquidity
        common_tokens = ["QX", "QUBIC", "QU"]
        if token_symbol.upper() in common_tokens:
            return "high_liquidity"
        
        # Check if we have stats already
        if token_symbol in self.token_stats:
            stat = self.token_stats[token_symbol]
            # High volume transactions might indicate high liquidity
            if stat.alerts_24h > 10:
                return "high_liquidity"
        
        return "normal_liquidity"
    
    def add_signal(self, signal: TokenSignal) -> None:
        """Store a new trading signal."""
        self.token_signals.appendleft(signal)
    
    def get_tokens_overview(self) -> List[TokenStats]:
        """Return a list of TokenStats for all known tokens."""
        return list(self.token_stats.values())
    
    def get_token_by_symbol(self, symbol: str) -> Optional[TokenStats]:
        """Return stats for a single token, or None if not tracked."""
        return self.token_stats.get(symbol)
    
    def get_recent_signals(self, limit: int = 20) -> List[TokenSignal]:
        """Return the most recent N token signals."""
        return list(self.token_signals)[:limit]

