import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { Activity, Box, Users } from "lucide-react"

interface NetworkStatsProps {
  tick?: number
}

export function NetworkStats({ tick = 0 }: NetworkStatsProps) {
  const stats = {
    tps: Math.floor(Math.random() * 500) + 1000,
    blockHeight: tick || 8923456,
    activeAgents: 47,
  }

  const statCards = [
    { title: "TPS", value: stats.tps.toLocaleString(), icon: Activity, color: "text-primary" },
    { title: "Block Height", value: stats.blockHeight.toLocaleString(), icon: Box, color: "text-primary" },
    { title: "Active Agents", value: stats.activeAgents, icon: Users, color: "text-primary" },
  ]

  return (
    <Card className="border-primary/30">
      <CardHeader>
        <CardTitle className="text-sm font-mono uppercase text-muted-foreground">Network Statistics</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4 sm:grid-cols-3">
        {statCards.map((stat) => {
          const Icon = stat.icon
          return (
            <div
              key={stat.title}
              className="flex items-center gap-4 rounded-md border border-border bg-secondary/50 p-4"
            >
              <Icon className={`h-8 w-8 ${stat.color}`} />
              <div>
                <p className="text-xs font-mono text-muted-foreground">{stat.title}</p>
                <p className="text-2xl font-bold text-foreground font-mono">{stat.value}</p>
              </div>
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}

