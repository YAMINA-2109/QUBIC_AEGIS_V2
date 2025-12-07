import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { ScrollArea } from "./ui/scroll-area";

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
}

interface TransactionFeedProps {
  transactions: RiskAnalysis[];
}

const formatTime = (timestamp: string | null | undefined): string => {
  if (!timestamp) return "Just now";
  try {
    const date = new Date(timestamp);
    if (isNaN(date.getTime())) return "Just now";
    const now = new Date();
    const diffSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    if (diffSeconds < 10) return "Just now";
    if (diffSeconds < 60) return `${diffSeconds}s ago`;
    if (diffSeconds < 3600) return `${Math.floor(diffSeconds / 60)}m ago`;
    return date.toLocaleTimeString("en-US", { hour12: false });
  } catch {
    return "Just now";
  }
};

export function TransactionFeed({ transactions }: TransactionFeedProps) {
  return (
    <Card className="border-primary/30">
      <CardHeader>
        <CardTitle className="text-sm font-mono uppercase text-muted-foreground">
          Live Transaction Feed
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border border-border bg-black/40 font-mono text-xs">
          <div className="grid grid-cols-7 gap-4 border-b border-border bg-secondary/50 px-4 py-2 font-semibold text-primary">
            <div>TIME</div>
            <div>TICK</div>
            <div>AMOUNT</div>
            <div>TOKEN</div>
            <div>TYPE</div>
            <div>SOURCE</div>
            <div className="text-right">RISK</div>
          </div>
          <ScrollArea className="h-[300px]">
            {transactions.length === 0 ? (
              <div className="p-4 text-center text-muted-foreground">
                Waiting for transactions...
              </div>
            ) : (
              transactions.map((tx, idx) => {
                const source = tx.transaction?.source || "RPC";
                const amount = tx.transaction?.amount ?? 0;
                const tick = tx.transaction?.tick ?? 0;
                const riskScore = tx.risk_score ?? 0;
                const type = tx.transaction?.type || "UNKNOWN";

                return (
                  <div
                    key={idx}
                    className="grid grid-cols-7 gap-4 border-b border-border/50 px-4 py-2 hover:bg-secondary/30 transition-colors"
                  >
                    <div className="text-muted-foreground">
                      {formatTime(tx.transaction?.timestamp)}
                    </div>
                    <div className="text-primary">#{tick}</div>
                    <div className="text-foreground font-bold">
                      {amount.toFixed(2)}
                    </div>
                    <div className="text-primary font-semibold">
                      {tx.transaction?.token_symbol || "—"}
                    </div>
                    <div className="text-foreground">{type.toUpperCase()}</div>
                    <div
                      className={`text-xs font-mono ${
                        source === "SIMULATION"
                          ? "text-yellow-500"
                          : "text-green-500"
                      }`}
                    >
                      {source}
                    </div>
                    <div
                      className={`text-right font-bold ${
                        riskScore > 70
                          ? "text-destructive"
                          : riskScore > 40
                          ? "text-yellow-500"
                          : "text-primary"
                      }`}
                    >
                      {riskScore.toFixed(1)}
                    </div>
                  </div>
                );
              })
            )}
          </ScrollArea>
        </div>
      </CardContent>
    </Card>
  );
}
