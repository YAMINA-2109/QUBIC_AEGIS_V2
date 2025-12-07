import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { apiUrl } from "../lib/api";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Search, TrendingUp, TrendingDown, Minus } from "lucide-react";

interface ForecastData {
  wallet_id: string;
  history: Array<{ timestamp: string; risk_score: number }>;
  forecast: Array<{ timestamp: string; predicted_risk: number }>;
  trend: "UP" | "DOWN" | "STABLE";
  error?: string;
}

interface GlobalPrediction {
  predicted_risk: number;
  confidence: number;
  trend: string;
  forecast: number[];
  horizon: string;
}

export function Predictions() {
  const [walletId, setWalletId] = useState("");
  const [forecastData, setForecastData] = useState<ForecastData | null>(null);
  const [globalPrediction, setGlobalPrediction] =
    useState<GlobalPrediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch global prediction on mount
  useEffect(() => {
    const fetchGlobalPrediction = async () => {
      try {
        const response = await fetch(apiUrl("api/predict?horizon=short_term"));
        const data = await response.json();
        setGlobalPrediction(data);
      } catch (err) {
        console.error("Error fetching global prediction:", err);
      }
    };

    fetchGlobalPrediction();
    const interval = setInterval(fetchGlobalPrediction, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const handleForecast = async () => {
    if (!walletId.trim()) {
      setError("Please enter a wallet ID");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${apiUrl("api/predict")}?wallet_id=${encodeURIComponent(
          walletId
        )}&horizon=short_term`
      );
      const data = await response.json();

      if (data.error) {
        setError(data.error);
        setForecastData(null);
      } else {
        setForecastData(data);
      }
    } catch (err) {
      setError(`Error: ${err}`);
      setForecastData(null);
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "UP":
        return <TrendingUp className="h-4 w-4 text-destructive" />;
      case "DOWN":
        return <TrendingDown className="h-4 w-4 text-primary" />;
      default:
        return <Minus className="h-4 w-4 text-yellow-500" />;
    }
  };

  // Prepare chart data
  const chartData = forecastData
    ? [
        ...forecastData.history.map((h) => ({
          time: new Date(h.timestamp).toLocaleTimeString("en-US", {
            hour12: false,
            hour: "2-digit",
            minute: "2-digit",
          }),
          historical: h.risk_score,
          predicted: null as number | null,
        })),
        ...forecastData.forecast.map((f) => ({
          time: new Date(f.timestamp).toLocaleTimeString("en-US", {
            hour12: false,
            hour: "2-digit",
            minute: "2-digit",
          }),
          historical: null as number | null,
          predicted: f.predicted_risk,
        })),
      ]
    : [];

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight font-mono">
          RISK PREDICTIONS & FORECASTING
        </h1>
        <p className="text-sm text-muted-foreground mt-2">
          AI-powered risk forecasting with per-wallet predictions
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Global Prediction */}
        <Card className="border-primary/30">
          <CardHeader>
            <CardTitle className="text-sm font-mono uppercase text-muted-foreground">
              Global Risk Prediction
            </CardTitle>
          </CardHeader>
          <CardContent>
            {globalPrediction ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-4xl font-bold text-primary font-mono">
                      {globalPrediction.predicted_risk.toFixed(1)}
                    </div>
                    <div className="text-sm text-muted-foreground mt-1">
                      Predicted Risk Score
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center gap-2">
                      {getTrendIcon(globalPrediction.trend)}
                      <span className="text-sm font-mono uppercase">
                        {globalPrediction.trend}
                      </span>
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      Confidence: {globalPrediction.confidence?.toFixed(0) || 0}
                      %
                    </div>
                  </div>
                </div>
                <div className="text-xs text-muted-foreground">
                  Horizon: {globalPrediction.horizon} | Based on network-wide
                  analysis
                </div>
              </div>
            ) : (
              <div className="text-muted-foreground">
                Loading global prediction...
              </div>
            )}
          </CardContent>
        </Card>

        {/* Wallet Forecast Input */}
        <Card className="border-primary/30">
          <CardHeader>
            <CardTitle className="text-sm font-mono uppercase text-muted-foreground">
              Per-Wallet Forecast
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex gap-2">
                <Input
                  placeholder="Enter wallet ID..."
                  value={walletId}
                  onChange={(e) => setWalletId(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleForecast()}
                  className="font-mono text-sm"
                />
                <Button onClick={handleForecast} disabled={loading}>
                  <Search className="h-4 w-4" />
                </Button>
              </div>
              {error && <div className="text-sm text-destructive">{error}</div>}
              {forecastData && !forecastData.error && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    {getTrendIcon(forecastData.trend)}
                    <span className="text-sm font-mono">
                      Trend: {forecastData.trend}
                    </span>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    History: {forecastData.history.length} points | Forecast:{" "}
                    {forecastData.forecast.length} points
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Forecast Chart */}
      {forecastData && !forecastData.error && chartData.length > 0 && (
        <Card className="border-primary/30 mt-6">
          <CardHeader>
            <CardTitle className="text-sm font-mono uppercase text-muted-foreground">
              Wallet Forecast: {forecastData.wallet_id.substring(0, 20)}...
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chartData}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="rgba(255,255,255,0.1)"
                />
                <XAxis
                  dataKey="time"
                  stroke="rgba(255,255,255,0.5)"
                  style={{ fontSize: "12px", fontFamily: "monospace" }}
                />
                <YAxis
                  stroke="rgba(255,255,255,0.5)"
                  style={{ fontSize: "12px", fontFamily: "monospace" }}
                  domain={[0, 100]}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "rgba(0,0,0,0.9)",
                    border: "1px solid rgba(0,255,100,0.3)",
                    borderRadius: "4px",
                    fontFamily: "monospace",
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="historical"
                  stroke="rgba(0,255,100,1)"
                  strokeWidth={2}
                  dot={false}
                  name="Historical Risk"
                />
                <Line
                  type="monotone"
                  dataKey="predicted"
                  stroke="rgba(255,50,50,0.8)"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={false}
                  name="Predicted Risk"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
