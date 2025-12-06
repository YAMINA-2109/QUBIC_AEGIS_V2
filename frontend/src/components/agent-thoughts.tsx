import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { ScrollArea } from "./ui/scroll-area"
import { Bot } from "lucide-react"

interface Thought {
  id: string
  agent: string
  message: string
  timestamp: string
}

interface AgentThoughtsProps {
  logs: string[]
}

export function AgentThoughts({ logs }: AgentThoughtsProps) {
  // Parse logs into thoughts format
  const thoughts: Thought[] = logs
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
              thoughts.map((thought) => (
                <div key={thought.id} className="flex gap-3">
                  <Bot className="h-5 w-5 shrink-0 text-primary mt-1" />
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-primary">{thought.agent}</span>
                      <span className="font-mono text-xs text-muted-foreground">{thought.timestamp}</span>
                    </div>
                    <p className="text-sm text-foreground">{thought.message}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}

