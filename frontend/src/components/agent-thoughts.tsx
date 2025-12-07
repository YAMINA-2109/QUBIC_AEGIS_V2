import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { ScrollArea } from "./ui/scroll-area"
import { Bot } from "lucide-react"

interface Thought {
  id: string
  agent: string
  message: string
  timestamp: string
}

interface Transaction {
  source_id: string;
  dest_id: string;
  amount: number;
  tick: number;
  type: string;
  timestamp: string | null;
  token_symbol?: string;
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
  attack_type?: string;
  prediction?: {
    predicted_risk?: number;
    trend?: string;
  };
  xai_explanation?: {
    xai_summary?: string;
    summary?: string;
  };
}

interface AgentThoughtsProps {
  logs: string[];
  transactions?: RiskAnalysis[];
  onLogClick?: (analysis: RiskAnalysis | null) => void;
}

export function AgentThoughts({ logs, transactions = [], onLogClick }: AgentThoughtsProps) {
  // Filter out error messages (WebSocket errors, disconnections)
  const filteredLogs = logs.filter((log) => {
    const lowerLog = log.toLowerCase();
    return (
      !lowerLog.includes("websocket connection error") &&
      !lowerLog.includes("disconnected") &&
      !lowerLog.includes("connection error") &&
      !lowerLog.includes("failed to connect")
    );
  });

  // Parse logs into thoughts format
  const thoughts: Thought[] = filteredLogs
    .slice()
    .reverse()
    .slice(0, 15)
    .map((log, idx) => {
      const match = log.match(/\[(.*?)\]\s*(.*)/)
      const timestamp = match ? match[1] : new Date().toLocaleTimeString()
      const message = match ? match[2] : log

      // Extract agent name from message if present
      const agentMatch = message.match(/(ANALYST|SENTINEL|GUARDIAN|ORACLE|NEXUS)-\d+/)
      const agent = agentMatch ? agentMatch[0] : "AEGIS-CORE"

      return {
        id: `${idx}-${Date.now()}`,
        agent,
        message: message.replace(/\[.*?\]\s*/, ""),
        timestamp,
      }
    })

  return (
    <Card className="border-primary/30">
      <CardHeader>
        <CardTitle className="text-sm font-mono uppercase text-muted-foreground">AI Agent Thoughts</CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[300px] rounded-md border border-border bg-black/40 p-4">
          <div className="space-y-4">
            {thoughts.length === 0 ? (
              <div className="text-muted-foreground text-sm">No agent activity yet...</div>
            ) : (
              thoughts.map((thought, idx) => {
                // Try to find matching transaction from transactions list
                const findMatchingTransaction = (): RiskAnalysis | null => {
                  // Extract tick from message to find matching transaction
                  const tickMatch = thought.message.match(/Tick\s+(\d+)/i);
                  if (tickMatch) {
                    const tick = parseInt(tickMatch[1]);
                    const matching = transactions.find(
                      (tx) => tx.transaction?.tick === tick
                    );
                    if (matching) return matching;
                  }

                  // Try to extract data from log message
                  const riskMatch = thought.message.match(/Score:\s*(\d+\.?\d*)/i);
                  const levelMatch = thought.message.match(/\[(LOW|MEDIUM|HIGH|CRITICAL)\]/i);
                  const tickMatch2 = thought.message.match(/Tick\s+(\d+)/i);
                  const amountMatch = thought.message.match(/Amount:\s*([\d,]+\.?\d*)/i);
                  const tokenMatch = thought.message.match(/(QXALPHA|QX|QUBIC)/i);

                  if (!riskMatch && !levelMatch && !thought.message.includes("XAI:")) {
                    return null;
                  }

                  // Create a compatible RiskAnalysis from log
                  return {
                    transaction: {
                      source_id: "EXTRACTED_FROM_LOG",
                      dest_id: "EXTRACTED_FROM_LOG",
                      amount: amountMatch ? parseFloat(amountMatch[1].replace(/,/g, "")) : 0,
                      tick: tickMatch2 ? parseInt(tickMatch2[1]) : 0,
                      type: "transfer",
                      timestamp: new Date().toISOString(),
                      token_symbol: tokenMatch ? tokenMatch[1].toUpperCase() : "QUBIC",
                      source: "RPC" as const,
                    },
                    risk_score: riskMatch ? parseFloat(riskMatch[1]) : 0,
                    risk_level: levelMatch ? levelMatch[1].toUpperCase() : "UNKNOWN",
                    explanation: thought.message,
                  };
                };

                const analysis = findMatchingTransaction();
                const isClickable = onLogClick && analysis;

                return (
                  <div 
                    key={thought.id} 
                    className={isClickable ? "flex gap-3 cursor-pointer hover:bg-secondary/20 p-2 rounded transition-colors" : "flex gap-3"}
                    onClick={() => isClickable && onLogClick?.(analysis)}
                  >
                    <Bot className="h-5 w-5 shrink-0 text-primary mt-1" />
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-primary">{thought.agent}</span>
                        <span className="font-mono text-xs text-muted-foreground">{thought.timestamp}</span>
                      </div>
                      <p className="text-sm text-foreground">{thought.message}</p>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}

