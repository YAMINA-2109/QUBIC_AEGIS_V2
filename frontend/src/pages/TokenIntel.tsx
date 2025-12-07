import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import {
  Loader2,
  TrendingUp,
  TrendingDown,
  Minus,
  AlertCircle,
  Activity,
  Filter,
  Search,
  Download,
} from "lucide-react";
import { cn } from "../lib/utils";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { SentimentGauge } from "../components/sentiment-gauge";
import { apiUrl } from "../lib/api";

interface TokenStats {
  symbol: string;
  name?: string;
  latest_risk_score: number;
  average_risk_24h: number;
  alerts_24h: number;
  trend: "UP" | "DOWN" | "STABLE";
  liquidity_tag?: string;
  risk_label?: string;
  last_updated: string;
}

interface TokenSignal {
  id: string;
  token_symbol: string;
  timestamp: string;
  signal_type: string;
  risk_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  message: string;
  xai_summary?: string;
}

interface MarketIntelData {
  tokens: TokenStats[];
  signals: TokenSignal[];
  generated_at: string;
}

// Demo data fallback for presentation
const getDemoMarketIntel = (): MarketIntelData => {
  const now = new Date();
  return {
    tokens: [
      {
        symbol: "QXALPHA",
        name: "Qubic Alpha Token",
        latest_risk_score: 45.3,
        average_risk_24h: 48.7,
        alerts_24h: 3,
        trend: "UP" as const,
        liquidity_tag: "HIGH",
        risk_label: "MODERATE",
        last_updated: now.toISOString(),
      },
      {
        symbol: "QX",
        name: "Qubic Token",
        latest_risk_score: 12.5,
        average_risk_24h: 15.2,
        alerts_24h: 0,
        trend: "STABLE" as const,
        liquidity_tag: "VERY_HIGH",
        risk_label: "SAFE",
        last_updated: now.toISOString(),
      },
    ],
    signals: [
      {
        id: "sig_001",
        token_symbol: "QXALPHA",
        timestamp: new Date(now.getTime() - 30000).toISOString(),
        signal_type: "WHALE_TRANSFER",
        risk_score: 78.5,
        risk_level: "HIGH" as const,
        message:
          "Large QXALPHA transfer detected - potential market manipulation",
      },
      {
        id: "sig_002",
        token_symbol: "QXT",
        timestamp: new Date(now.getTime() - 60000).toISOString(),
        signal_type: "VOLATILITY_SPIKE",
        risk_score: 65.2,
        risk_level: "MEDIUM" as const,
        message: "Unusual volatility detected in QXT trading pairs",
      },
    ],
    generated_at: now.toISOString(),
  };
};

export function TokenIntel() {
  const [data, setData] = useState<MarketIntelData | null>(
    getDemoMarketIntel()
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState<"risk" | "alerts" | "trend">("risk");
  const [filterRisk, setFilterRisk] = useState<"all" | "high" | "critical">(
    "all"
  );

  const fetchMarketIntel = async () => {
    try {
      const response = await fetch(apiUrl("api/market-intel/overview"));
      if (!response.ok) {
        throw new Error("Failed to fetch market intelligence");
      }
      const marketData: MarketIntelData = await response.json();
      setData(marketData);
      setError(null);
    } catch (err) {
      console.error("Error fetching market intel:", err);
      setError(err instanceof Error ? err.message : "Unknown error");
      // Keep demo data on error
      setData(getDemoMarketIntel());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMarketIntel();
    // Refresh every 2 seconds
    const interval = setInterval(fetchMarketIntel, 2000);
    return () => clearInterval(interval);
  }, []);

  const getRiskColor = (risk: number) => {
    if (risk >= 70) return "text-destructive";
    if (risk >= 40) return "text-orange-500";
    if (risk >= 20) return "text-yellow-500";
    return "text-primary";
  };

  const getRiskBorderClass = (risk: number) => {
    if (risk >= 70) {
      return "border-destructive cyber-glow-red";
    }
    return "border-primary/30";
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "UP":
        return <TrendingUp className="h-4 w-4 text-red-500" />;
      case "DOWN":
        return <TrendingDown className="h-4 w-4 text-primary" />;
      default:
        return <Minus className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getRiskBadgeClass = (riskLevel: string) => {
    switch (riskLevel) {
      case "CRITICAL":
        return "bg-red-500/20 text-red-400 border-red-500/50";
      case "HIGH":
        return "bg-orange-500/20 text-orange-400 border-orange-500/50";
      case "MEDIUM":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/50";
      default:
        return "bg-primary/20 text-primary border-primary/50";
    }
  };

  const formatTime = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      if (isNaN(date.getTime())) return "Just now";
      const now = new Date();
      const diffSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
      if (diffSeconds < 10) return "Just now";
      if (diffSeconds < 60) return `${diffSeconds}s ago`;
      return date.toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false,
      });
    } catch {
      return "Just now";
    }
  };

  if (loading && !data) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-12 w-12 animate-spin text-primary" />
          <p className="text-sm font-mono text-muted-foreground">
            LOADING MARKET INTELLIGENCE...
          </p>
        </div>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="flex h-full items-center justify-center">
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5" />
              <p className="font-mono">Error: {error}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col gap-6 overflow-auto p-6 bg-[#050505]">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold font-mono text-[#00ff41] flex items-center gap-3">
            <Activity className="h-8 w-8" />
            MARKET INTELLIGENCE
          </h1>
          <p className="mt-1 text-sm text-gray-400 font-mono">
            Real-time token analysis & trading signals
          </p>
        </div>
        {data && (
          <div className="text-right">
            <p className="text-xs font-mono text-gray-400">LAST UPDATE</p>
            <p className="text-sm font-mono text-[#00ff41]">
              {formatTime(data.generated_at)}
            </p>
          </div>
        )}
      </div>

      {/* Network Sentiment Gauge */}
      {(() => {
        // Calculate sentiment score from tokens (0-100: 0 = Panic, 100 = Greed)
        // Lower risk = higher sentiment (greed), Higher risk = lower sentiment (fear)
        const sentimentScore = data
          ? Math.max(
              0,
              Math.min(
                100,
                data.tokens.length > 0
                  ? data.tokens.reduce(
                      (sum, t) => sum + (100 - t.latest_risk_score),
                      0
                    ) / data.tokens.length
                  : 50
              )
            )
          : 55; // Default to slightly positive sentiment

        return <SentimentGauge sentimentScore={sentimentScore} />;
      })()}

      {/* Section 1: Top Assets Grid */}
      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold font-mono uppercase text-muted-foreground">
            TOP ASSETS
          </h2>
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Search token..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8 w-48 h-8 text-xs font-mono border-primary/30 bg-background"
              />
            </div>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="h-8 px-2 text-xs font-mono border border-primary/30 bg-background rounded text-foreground"
            >
              <option value="risk">Sort by Risk</option>
              <option value="alerts">Sort by Alerts</option>
              <option value="trend">Sort by Trend</option>
            </select>
            <select
              value={filterRisk}
              onChange={(e) => setFilterRisk(e.target.value as any)}
              className="h-8 px-2 text-xs font-mono border border-primary/30 bg-background rounded text-foreground"
            >
              <option value="all">All Risks</option>
              <option value="high">High Risk Only</option>
              <option value="critical">Critical Only</option>
            </select>
          </div>
        </div>
        {loading && data && (
          <div className="mb-4 flex items-center justify-center">
            <Loader2 className="h-4 w-4 animate-spin text-primary mr-2" />
            <span className="text-xs font-mono text-muted-foreground">
              Updating...
            </span>
          </div>
        )}
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {data?.tokens
            .filter((token) => {
              if (
                searchQuery &&
                !token.symbol.toLowerCase().includes(searchQuery.toLowerCase())
              )
                return false;
              if (filterRisk === "high" && token.latest_risk_score < 70)
                return false;
              if (filterRisk === "critical" && token.latest_risk_score < 90)
                return false;
              return true;
            })
            .sort((a, b) => {
              if (sortBy === "risk")
                return b.latest_risk_score - a.latest_risk_score;
              if (sortBy === "alerts") return b.alerts_24h - a.alerts_24h;
              if (sortBy === "trend") {
                const trendOrder = { UP: 3, DOWN: 1, STABLE: 2 };
                return (trendOrder[b.trend] || 2) - (trendOrder[a.trend] || 2);
              }
              return 0;
            })
            .map((token) => (
              <Card
                key={token.symbol}
                className={cn(
                  "border-2 transition-all duration-300 hover:border-primary/60",
                  getRiskBorderClass(token.latest_risk_score)
                )}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg font-bold font-mono text-primary">
                      {token.symbol}
                    </CardTitle>
                    {getTrendIcon(token.trend)}
                  </div>
                  {token.name && (
                    <p className="text-xs text-muted-foreground font-mono">
                      {token.name}
                    </p>
                  )}
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <p className="text-xs font-mono uppercase text-muted-foreground mb-1">
                      Risk Score
                    </p>
                    <div className="flex items-baseline gap-2">
                      <span
                        className={cn(
                          "text-2xl font-bold font-mono",
                          getRiskColor(token.latest_risk_score)
                        )}
                      >
                        {token.latest_risk_score.toFixed(1)}
                      </span>
                      <span className="text-xs text-muted-foreground font-mono">
                        /100
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-xs font-mono">
                    <div>
                      <span className="text-muted-foreground">Trend:</span>
                      <span
                        className={cn(
                          "ml-2 font-semibold",
                          token.trend === "UP"
                            ? "text-red-500"
                            : token.trend === "DOWN"
                            ? "text-primary"
                            : "text-muted-foreground"
                        )}
                      >
                        {token.trend}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Alerts:</span>
                      <span className="ml-2 font-semibold text-primary">
                        {token.alerts_24h}
                      </span>
                    </div>
                  </div>

                  {token.risk_label && (
                    <div className="pt-2 border-t border-border">
                      <span className="text-xs font-mono text-muted-foreground">
                        Status:{" "}
                        <span className="text-primary">{token.risk_label}</span>
                      </span>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
        </div>
      </div>

      {/* Section 2: Live Signals Terminal */}
      <div className="flex-1">
        <h2 className="mb-4 text-lg font-bold font-mono uppercase text-muted-foreground">
          LIVE SIGNALS TERMINAL
        </h2>
        <Card className="border border-primary/30 bg-card">
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full border-collapse font-mono text-xs">
                <thead>
                  <tr className="border-b border-primary/30 bg-card/50">
                    <th className="px-4 py-3 text-left text-muted-foreground font-semibold uppercase">
                      Time
                    </th>
                    <th className="px-4 py-3 text-left text-muted-foreground font-semibold uppercase">
                      Token
                    </th>
                    <th className="px-4 py-3 text-left text-muted-foreground font-semibold uppercase">
                      Signal Type
                    </th>
                    <th className="px-4 py-3 text-left text-muted-foreground font-semibold uppercase">
                      Risk Level
                    </th>
                    <th className="px-4 py-3 text-left text-muted-foreground font-semibold uppercase">
                      Message
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {data?.signals.length === 0 ? (
                    <tr>
                      <td
                        colSpan={5}
                        className="px-4 py-8 text-center text-muted-foreground"
                      >
                        No signals detected
                      </td>
                    </tr>
                  ) : (
                    data?.signals.map((signal, index) => (
                      <tr
                        key={signal.id}
                        className={cn(
                          "border-b border-border/50 transition-colors hover:bg-card/50",
                          index % 2 === 0 ? "bg-card/30" : "bg-card"
                        )}
                      >
                        <td className="px-4 py-3 text-muted-foreground">
                          {formatTime(signal.timestamp)}
                        </td>
                        <td className="px-4 py-3">
                          <span className="font-bold text-primary">
                            {signal.token_symbol}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-muted-foreground">
                          {signal.signal_type.replace(/_/g, " ")}
                        </td>
                        <td className="px-4 py-3">
                          <span
                            className={cn(
                              "inline-flex items-center rounded border px-2 py-0.5 text-xs font-semibold",
                              getRiskBadgeClass(signal.risk_level)
                            )}
                          >
                            {signal.risk_level}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-foreground max-w-md truncate">
                          {signal.message}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
