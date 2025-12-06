import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { ScrollArea } from "./ui/scroll-area"

interface Transaction {
  source_id: string
  dest_id: string
  amount: number
  tick: number
  type: string
  timestamp: string | null
  token_symbol?: string
  token_name?: string
}

interface RiskAnalysis {
  transaction: Transaction
  risk_score: number
  risk_level: string
}

interface TransactionFeedProps {
  transactions: RiskAnalysis[]
}

export function TransactionFeed({ transactions }: TransactionFeedProps) {
  return (
    <Card className="border-primary/30">
      <CardHeader>
        <CardTitle className="text-sm font-mono uppercase text-muted-foreground">Live Transaction Feed</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border border-border bg-black/40 font-mono text-xs">
          <div className="grid grid-cols-6 gap-4 border-b border-border bg-secondary/50 px-4 py-2 font-semibold text-primary">
            <div>TIME</div>
            <div>TICK</div>
            <div>AMOUNT</div>
            <div>TOKEN</div>
            <div>TYPE</div>
            <div className="text-right">RISK</div>
          </div>
          <ScrollArea className="h-[300px]">
            {transactions.length === 0 ? (
              <div className="p-4 text-center text-muted-foreground">
                Waiting for transactions...
              </div>
            ) : (
              transactions.map((tx, idx) => (
                <div
                  key={idx}
                  className="grid grid-cols-6 gap-4 border-b border-border/50 px-4 py-2 hover:bg-secondary/30 transition-colors"
                >
                  <div className="text-muted-foreground">
                    {tx.transaction.timestamp
                      ? new Date(tx.transaction.timestamp).toLocaleTimeString("en-US", { hour12: false })
                      : "—"}
                  </div>
                  <div className="text-primary">#{tx.transaction.tick}</div>
                  <div className="text-foreground font-bold">{tx.transaction.amount.toFixed(2)}</div>
                  <div className="text-primary font-semibold">
                    {tx.transaction.token_symbol || "—"}
                  </div>
                  <div className="text-foreground">{tx.transaction.type.toUpperCase()}</div>
                  <div
                    className={`text-right font-bold ${
                      tx.risk_score > 70
                        ? "text-destructive"
                        : tx.risk_score > 40
                        ? "text-yellow-500"
                        : "text-primary"
                    }`}
                  >
                    {tx.risk_score.toFixed(1)}
                  </div>
                </div>
              ))
            )}
          </ScrollArea>
        </div>
      </CardContent>
    </Card>
  )
}

