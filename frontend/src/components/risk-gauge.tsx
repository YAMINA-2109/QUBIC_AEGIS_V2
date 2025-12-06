import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"

interface RiskGaugeProps {
  score: number
}

export function RiskGauge({ score }: RiskGaugeProps) {
  const isHighRisk = score > 80
  const rotation = (score / 100) * 180 - 90

  return (
    <Card className={`border-2 ${isHighRisk ? "border-destructive cyber-glow-red" : "border-primary/30"}`}>
      <CardHeader>
        <CardTitle className="text-sm font-mono uppercase text-muted-foreground">Current Risk Score</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col items-center justify-center pb-8">
        <div className="relative h-48 w-48">
          <svg viewBox="0 0 200 120" className="w-full">
            <defs>
              <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="rgb(0, 255, 100)" />
                <stop offset="50%" stopColor="rgb(255, 200, 0)" />
                <stop offset="100%" stopColor="rgb(255, 50, 50)" />
              </linearGradient>
            </defs>

            <path
              d="M 20 100 A 80 80 0 0 1 180 100"
              fill="none"
              stroke="url(#gaugeGradient)"
              strokeWidth="12"
              strokeLinecap="round"
              opacity="0.3"
            />

            <path
              d="M 20 100 A 80 80 0 0 1 180 100"
              fill="none"
              stroke={isHighRisk ? "rgb(255, 50, 50)" : "rgb(0, 255, 100)"}
              strokeWidth="12"
              strokeLinecap="round"
              strokeDasharray={`${(score / 100) * 251.2} 251.2`}
              className="transition-all duration-1000"
              style={{
                filter: isHighRisk ? "drop-shadow(0 0 8px rgb(255, 50, 50))" : "drop-shadow(0 0 8px rgb(0, 255, 100))",
              }}
            />

            <line
              x1="100"
              y1="100"
              x2="100"
              y2="30"
              stroke={isHighRisk ? "rgb(255, 50, 50)" : "rgb(0, 255, 100)"}
              strokeWidth="3"
              strokeLinecap="round"
              transform={`rotate(${rotation} 100 100)`}
              className="transition-transform duration-1000"
              style={{
                filter: isHighRisk ? "drop-shadow(0 0 6px rgb(255, 50, 50))" : "drop-shadow(0 0 6px rgb(0, 255, 100))",
              }}
            />

            <circle cx="100" cy="100" r="8" fill={isHighRisk ? "rgb(255, 50, 50)" : "rgb(0, 255, 100)"} />
          </svg>
        </div>

        <div className="mt-4 text-center">
          <div
            className={`text-6xl font-bold ${isHighRisk ? "text-destructive" : "text-primary"} font-mono`}
          >
            {Math.round(score)}
          </div>
          <div className="mt-2 text-sm font-mono uppercase text-muted-foreground">
            {isHighRisk ? "HIGH RISK" : score > 50 ? "MODERATE RISK" : "LOW RISK"}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

