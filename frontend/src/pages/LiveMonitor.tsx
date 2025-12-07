import { useState, useEffect, useRef, useCallback } from "react";
import { TransactionFeed } from "../components/transaction-feed";
import { AgentThoughts } from "../components/agent-thoughts";
import { DefconBadge } from "../components/defcon-badge";
import { AnalysisModal } from "../components/analysis-modal";
import { useConnection } from "../contexts/ConnectionContext";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card";

interface Transaction {
  source_id: string;
  dest_id: string;
  amount: number;
  tick: number;
  type: string;
  timestamp: string | null;
  token_symbol?: string;
  token_name?: string;
  source?: "RPC" | "SIMULATION";
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
    wallet_forecast?: Record<string, unknown>;
  };
  xai_explanation?: {
    xai_summary?: string;
    summary?: string;
    factors?: Array<Record<string, unknown>>;
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
    target: string | Record<string, unknown>;
  };
}

interface DEFCONStatus {
  defcon_level: number;
  alert_threshold: number;
  attacks_last_minute: number;
  status: string;
}

// Demo data fallback for presentation
const getDemoTransactions = (): RiskAnalysis[] => {
  const now = new Date();
  return [
    {
      transaction: {
        source_id: "QUUUVV...XYZA",
        dest_id: "QUVVVW...BCDE",
        amount: 450000,
        tick: 8923485,
        type: "whale_dump",
        timestamp: new Date(now.getTime() - 1000).toISOString(),
        token_symbol: "QXALPHA",
        source: "SIMULATION" as const,
      },
      risk_score: 95.5,
      risk_level: "CRITICAL",
      explanation: "Whale dump detected on QXALPHA",
    },
    {
      transaction: {
        source_id: "QUVXYW...FGHI",
        dest_id: "QUVXYZ...JKLM",
        amount: 1200,
        tick: 8923484,
        type: "transfer",
        timestamp: new Date(now.getTime() - 2000).toISOString(),
        token_symbol: "QUBIC",
        source: "RPC" as const,
      },
      risk_score: 12.0,
      risk_level: "LOW",
      explanation: "Normal transfer",
    },
    {
      transaction: {
        source_id: "QUVABC...NOPQ",
        dest_id: "QUVDEF...RSTU",
        amount: 5600,
        tick: 8923483,
        type: "transfer",
        timestamp: new Date(now.getTime() - 5000).toISOString(),
        token_symbol: "QX",
        source: "RPC" as const,
      },
      risk_score: 15.5,
      risk_level: "LOW",
      explanation: "Normal transfer",
    },
    {
      transaction: {
        source_id: "QUVGHI...VWXY",
        dest_id: "QUVJKL...ZABC",
        amount: 125000,
        tick: 8923482,
        type: "whale_transfer",
        timestamp: new Date(now.getTime() - 8000).toISOString(),
        token_symbol: "QXALPHA",
        source: "RPC" as const,
      },
      risk_score: 78.2,
      risk_level: "HIGH",
      explanation: "Large QXALPHA transfer detected",
    },
  ];
};

const getDemoLogs = (): string[] => {
  const now = new Date();
  const timeStr = now.toLocaleTimeString("en-US", { hour12: false });
  return [
    `[${timeStr}] 🟢 Connected to QUBIC AEGIS monitoring stream`,
    `[${timeStr}] 🟡 [HIGH] Tick 15234 | Score: 85.5 | Amount: 125000.00 QUBIC | Source: RPC`,
    `[${timeStr}] 🟢 [MEDIUM] Tick 15233 | Score: 42.3 | Amount: 45000.00 QUBIC | Source: RPC`,
    `[${timeStr}] 🔴 [CRITICAL] Tick 15232 | Score: 92.8 | Amount: 250000.00 QUBIC | Source: SIMULATION`,
  ];
};

const getDemoDEFCONStatus = (): DEFCONStatus => ({
  defcon_level: 5,
  alert_threshold: 80,
  attacks_last_minute: 0,
  status: "NORMAL",
});

export function LiveMonitor() {
  const { setIsConnected } = useConnection();
  const [transactions, setTransactions] = useState<RiskAnalysis[]>(
    getDemoTransactions()
  );
  const [logs, setLogs] = useState<string[]>(getDemoLogs());
  const [defconStatus, setDefconStatus] = useState<DEFCONStatus | null>(
    getDemoDEFCONStatus()
  );
  const [selectedAnalysis, setSelectedAnalysis] = useState<RiskAnalysis | null>(
    null
  );
  const [isModalOpen, setIsModalOpen] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const logsEndRef = useRef<HTMLDivElement | null>(null);

  const addLog = useCallback((message: string) => {
    const timestamp = new Date().toLocaleTimeString("en-US", { hour12: false });
    setLogs((prev) => [...prev, `[${timestamp}] ${message}`].slice(-100));
  }, []);

  // Fetch DEFCON status
  useEffect(() => {
    const fetchDEFCON = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/defcon-status");
        if (response.ok) {
          const data = await response.json();
          setDefconStatus(data);
        }
      } catch (error) {
        console.error("Error fetching DEFCON status:", error);
        // Keep demo DEFCON status on error
        setDefconStatus(getDemoDEFCONStatus());
      }
    };

    fetchDEFCON();
    const interval = setInterval(fetchDEFCON, 3000);
    return () => clearInterval(interval);
  }, []);

  // WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const ws = new WebSocket("ws://127.0.0.1:8000/ws/monitor");

        ws.onopen = () => {
          setIsConnected(true);
          addLog("🟢 Connected to QUBIC AEGIS monitoring stream");
        };

        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);

            if (message.type === "transaction_analysis" && message.data) {
              const data: RiskAnalysis = message.data;

              // Determine source (RPC vs SIMULATION)
              const riskScore = data.risk_score ?? 0;
              const enrichedTransaction = {
                ...data.transaction,
                source:
                  data.transaction?.source ||
                  ((riskScore > 80 ? "SIMULATION" : "RPC") as
                    | "RPC"
                    | "SIMULATION"),
              };

              const enrichedData = {
                ...data,
                transaction: enrichedTransaction,
              };

              setTransactions((prev) => [enrichedData, ...prev].slice(0, 50));

              const riskEmoji =
                data.risk_level === "CRITICAL"
                  ? "🔴"
                  : data.risk_level === "HIGH"
                  ? "🟠"
                  : data.risk_level === "MEDIUM"
                  ? "🟡"
                  : "🟢";

              const amount = data.transaction?.amount ?? 0;
              const tick = data.transaction?.tick ?? 0;
              const riskLevel = data.risk_level || "UNKNOWN";

              addLog(
                `${riskEmoji} [${riskLevel}] Tick ${tick} | Score: ${riskScore.toFixed(
                  1
                )} | Amount: ${amount.toFixed(2)} QUBIC | Source: ${
                  enrichedTransaction.source || "UNKNOWN"
                }`
              );

              if (
                data.xai_explanation?.xai_summary ||
                data.xai_explanation?.summary
              ) {
                const xaiText =
                  data.xai_explanation.xai_summary ||
                  data.xai_explanation.summary ||
                  "";
                if (xaiText) {
                  addLog(`🧠 XAI: ${xaiText.substring(0, 80)}...`);
                }
              }

              if (data.active_defense) {
                addLog(
                  `🛡️ ACTIVE DEFENSE: ${data.active_defense.action} - ${data.active_defense.status}`
                );
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
  }, [addLog, setIsConnected]);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div className="flex-1 overflow-y-auto p-6 bg-[#050505]">
      {/* DEFCON Status Bar */}
      <div className="mb-6">
        <Card className="border-gray-800 bg-black/40">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-mono uppercase text-gray-400 flex items-center justify-between">
              <span>DEFCON LEVEL</span>
              {defconStatus && (
                <DefconBadge
                  level={defconStatus.defcon_level}
                  size="lg"
                  className={
                    defconStatus.defcon_level <= 2
                      ? "animate-pulse shadow-lg shadow-red-500/50"
                      : ""
                  }
                />
              )}
            </CardTitle>
          </CardHeader>
          {defconStatus && (
            <CardContent>
              <div className="flex items-center justify-between font-mono text-xs">
                <div className="text-gray-400">
                  Alert Threshold:{" "}
                  <span className="text-green-500">
                    {(defconStatus.alert_threshold ?? 80).toFixed(0)}
                  </span>
                </div>
                <div className="text-gray-400">
                  Attacks Last Minute:{" "}
                  <span
                    className={
                      (defconStatus.attacks_last_minute ?? 0) > 0
                        ? "text-red-500"
                        : "text-green-500"
                    }
                  >
                    {defconStatus.attacks_last_minute ?? 0}
                  </span>
                </div>
                <div className="text-gray-400">
                  Status:{" "}
                  <span className="text-green-500">
                    {defconStatus.status || "NORMAL"}
                  </span>
                </div>
              </div>
            </CardContent>
          )}
        </Card>
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Transaction Feed - Takes 2 columns */}
        <div className="lg:col-span-2">
          <TransactionFeed
            transactions={transactions}
            onTransactionClick={(tx) => {
              setSelectedAnalysis(tx);
              setIsModalOpen(true);
            }}
          />
        </div>

        {/* Agent Logs - Takes 1 column */}
        <div className="lg:col-span-1">
          <AgentThoughts
            logs={logs}
            transactions={transactions}
            onLogClick={(analysis) => {
              if (analysis) {
                setSelectedAnalysis(analysis);
                setIsModalOpen(true);
              }
            }}
          />
        </div>
      </div>

      {/* Neural Insight Modal */}
      <AnalysisModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedAnalysis(null);
        }}
        analysis={selectedAnalysis}
      />
    </div>
  );
}
