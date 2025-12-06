import { useState, useEffect, useRef, useCallback } from "react";
import { RiskGauge } from "../components/risk-gauge";
import { NetworkStats } from "../components/network-stats";
import { TransactionFeed } from "../components/transaction-feed";
import { AgentThoughts } from "../components/agent-thoughts";
import { RiskChart } from "../components/risk-chart";
import { DEFCONWidget } from "../components/defcon-widget";
import { Button } from "../components/ui/button";
import { AlertTriangle, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { useConnection } from "../contexts/ConnectionContext";

interface Transaction {
  source_id: string;
  dest_id: string;
  amount: number;
  tick: number;
  type: string;
  timestamp: string | null;
  token_symbol?: string;
  token_name?: string;
}

interface RiskAnalysis {
  transaction: Transaction;
  risk_score: number;
  risk_level: string;
  explanation?: string;
  risk_factors?: Array<{
    factor: string;
    severity: string;
    details?: string;
    impact?: number;
  }>;
  prediction?: {
    predicted_risk?: number;
    trend?: string;
    wallet_forecast?: any;
  };
  xai_explanation?: {
    xai_summary?: string;
    summary?: string;
    factors?: Array<any>;
  };
  defcon_status?: {
    defcon_level: number;
    alert_threshold: number;
    attacks_last_minute: number;
    status: string;
  };
  sentiment_analysis?: {
    sentiment_score: number;
    sentiment_label: string;
    correlation_with_risk: string;
    analysis: string;
  };
  active_defense?: {
    action: string;
    status: string;
    target: any;
  };
}

interface RiskHistoryData {
  time: string;
  risk: number;
}

export function Dashboard() {
  const { isConnected, setIsConnected } = useConnection();
  const [riskScore, setRiskScore] = useState<number>(0);
  const [transactions, setTransactions] = useState<RiskAnalysis[]>([]);
  const [logs, setLogs] = useState<string[]>([]);
  const [riskHistory, setRiskHistory] = useState<RiskHistoryData[]>([]);
  const [isAutomating, setIsAutomating] = useState<boolean>(false);
  const wsRef = useRef<WebSocket | null>(null);
  const logsEndRef = useRef<HTMLDivElement | null>(null);

  const addLog = useCallback((message: string) => {
    const timestamp = new Date().toLocaleTimeString("en-US", { hour12: false });
    setLogs((prev) => [...prev, `[${timestamp}] ${message}`].slice(-100));
  }, []);

  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const ws = new WebSocket("ws://localhost:8000/ws/monitor");

        ws.onopen = () => {
          setIsConnected(true);
          addLog("🟢 Connected to QUBIC AEGIS monitoring stream");
        };

        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);

            if (message.type === "transaction_analysis" && message.data) {
              const data: RiskAnalysis = message.data;

              setRiskScore(data.risk_score);

              setTransactions((prev) => [data, ...prev].slice(0, 20));

              const now = new Date().toLocaleTimeString("en-US", {
                hour: "2-digit",
                minute: "2-digit",
                hour12: false,
              });
              setRiskHistory((prev) =>
                [...prev, { time: now, risk: data.risk_score }].slice(-30)
              );

              const riskEmoji =
                data.risk_level === "CRITICAL"
                  ? "🔴"
                  : data.risk_level === "HIGH"
                  ? "🟠"
                  : data.risk_level === "MEDIUM"
                  ? "🟡"
                  : "🟢";
              
              // Enhanced log with prediction info
              const predictionInfo = data.prediction?.predicted_risk 
                ? ` | Predicted: ${data.prediction.predicted_risk.toFixed(1)} (${data.prediction.trend || 'STABLE'})`
                : "";
              
              addLog(
                `${riskEmoji} [${data.risk_level}] Tick ${data.transaction.tick} | Score: ${data.risk_score.toFixed(
                  1
                )}${predictionInfo} | Amount: ${data.transaction.amount.toFixed(2)} QUBIC`
              );
              
              // Log XAI explanation if available
              if (data.xai_explanation?.xai_summary || data.xai_explanation?.summary) {
                const xaiText = data.xai_explanation.xai_summary || data.xai_explanation.summary || "";
                if (xaiText) {
                  addLog(`🧠 XAI: ${xaiText.substring(0, 80)}...`);
                }
              }
              
              // Log sentiment analysis if available
              if (data.sentiment_analysis) {
                const sentiment = data.sentiment_analysis;
                addLog(`💭 Sentiment: ${sentiment.sentiment_label} (${sentiment.correlation_with_risk})`);
              }
              
              // Log active defense if triggered
              if (data.active_defense) {
                addLog(`🛡️ ACTIVE DEFENSE: ${data.active_defense.action} - ${data.active_defense.status}`);
              }
              
              // Log DEFCON changes if significant
              if (data.defcon_status && data.defcon_status.defcon_level <= 2) {
                addLog(`🚨 DEFCON ${data.defcon_status.defcon_level}: Maximum Alert Mode Activated`);
              }
            } else if (message.type === "connection") {
              addLog(`ℹ️ ${message.message}`);
            }
          } catch (error) {
            console.error("Error parsing WebSocket message:", error);
          }
        };

        ws.onerror = (error) => {
          console.error("WebSocket error:", error);
          setIsConnected(false);
          addLog("❌ WebSocket connection error");
        };

        ws.onclose = () => {
          setIsConnected(false);
          addLog("🔴 Disconnected from monitoring stream");
          setTimeout(connectWebSocket, 3000);
        };

        wsRef.current = ws;
      } catch (error) {
        console.error("Failed to connect WebSocket:", error);
        setIsConnected(false);
        addLog(
          "❌ Failed to connect to backend. Make sure the server is running on port 8000"
        );
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [addLog]);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const handleTriggerAutomation = async () => {
    const webhookUrl =
      "https://qubicaegis.app.n8n.cloud/webhook-test/bc96d8cb-43f8-4447-9fc9-d93abc18e4b0";

    setIsAutomating(true);
    toast.loading("Analyzing threat patterns...", { id: "automation" });

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/trigger-automation",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            webhook_url: webhookUrl,
            message: `QUBIC AEGIS Alert: Suspicious transaction detected\nRisk Score: ${riskScore.toFixed(
              1
            )}\nRisk Level: ${
              riskScore > 80 ? "CRITICAL" : riskScore > 40 ? "HIGH" : "MEDIUM"
            }`,
          }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        toast.success(
          "✅ Threat isolated! Protocols initiated via EasyConnect.",
          {
            id: "automation",
            duration: 4000,
            description:
              "Discord notification sent. Automation workflow activated.",
          }
        );
        addLog("✅ Automation triggered successfully - n8n workflow activated");
      } else {
        toast.error(`❌ Automation failed: ${data.detail || "Unknown error"}`, {
          id: "automation",
          duration: 4000,
        });
        addLog(
          `❌ Automation trigger failed: ${data.detail || "Unknown error"}`
        );
      }
    } catch (error) {
      toast.error(`❌ Error: ${error}`, {
        id: "automation",
        duration: 4000,
      });
      addLog(`❌ Error triggering automation: ${error}`);
    } finally {
      setTimeout(() => setIsAutomating(false), 2000);
    }
  };

  const isHighRisk = riskScore > 80;

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight font-mono">
          COMMAND CENTER
        </h1>
        <Button
          onClick={handleTriggerAutomation}
          disabled={isAutomating}
          className={`bg-destructive hover:bg-destructive/90 text-destructive-foreground font-bold text-lg px-8 py-6 transition-all ${
            isHighRisk ? "cyber-glow-red" : ""
          } ${isAutomating ? "opacity-75 cursor-not-allowed" : ""}`}
        >
          {isAutomating ? (
            <>
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              ANALYZING THREAT...
            </>
          ) : (
            <>
              <AlertTriangle className="mr-2 h-5 w-5" />
              TRIGGER AUTOMATION
            </>
          )}
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div className="lg:col-span-1">
          <RiskGauge score={riskScore} />
        </div>

        <div className="lg:col-span-1">
          <DEFCONWidget />
        </div>

        <div className="lg:col-span-1">
          <NetworkStats tick={transactions[0]?.transaction.tick || 0} />
        </div>

        <div className="lg:col-span-2">
          <TransactionFeed transactions={transactions} />
        </div>

        <div className="lg:col-span-1">
          <AgentThoughts logs={logs} />
        </div>

        <div className="lg:col-span-3">
          <RiskChart
            data={riskHistory.map((item) => ({
              time: item.time,
              risk: item.risk,
            }))}
          />
        </div>
      </div>
    </div>
  );
}

