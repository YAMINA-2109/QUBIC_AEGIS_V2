import { useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { ScrollArea } from "../components/ui/scroll-area";
import { apiUrl } from "../lib/api";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { AlertTriangle, Play, Loader2 } from "lucide-react";
import { toast } from "sonner";

interface SimulationStep {
  tick: number;
  description: string;
  affected_wallets: string[];
  risk_score: number;
}

interface SimulationResult {
  scenario: string;
  steps: SimulationStep[];
  peak_risk: number;
  estimated_impact: string;
  aegis_recommendation: string;
  description?: string;
  error?: string;
}

const SCENARIOS = [
  "whale_dump",
  "wash_trade",
  "flash_attack",
  "wallet_drain",
  "spam_attack",
  "liquidity_manipulation",
];

export function Simulator() {
  const [selectedScenario, setSelectedScenario] = useState("whale_dump");
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSimulate = async () => {
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(apiUrl("api/simulate"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          scenario_type: selectedScenario,
          parameters: {
            amount: 1000000,
            duration_minutes: 30,
          },
        }),
      });

      const data = await response.json();

      if (data.error) {
        toast.error(`Simulation error: ${data.error}`);
        setResult({ ...data, scenario: selectedScenario });
      } else {
        setResult(data);
        toast.success(`Simulation complete: ${data.scenario}`);
      }
    } catch (error) {
      toast.error(`Error: ${error}`);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case "Critical":
        return "text-destructive";
      case "High":
        return "text-red-500";
      case "Medium":
        return "text-yellow-500";
      default:
        return "text-primary";
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight font-mono">
          ATTACK SIMULATOR
        </h1>
        <p className="text-sm text-muted-foreground mt-2">
          AI-powered attack scenario simulation with step-by-step breakdown
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Control Panel */}
        <Card className="border-primary/30">
          <CardHeader>
            <CardTitle className="text-sm font-mono uppercase text-muted-foreground">
              Simulation Control
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-mono text-muted-foreground mb-2 block">
                Attack Scenario
              </label>
              <Select
                value={selectedScenario}
                onValueChange={(newValue) => {
                  setSelectedScenario(newValue);
                }}
              >
                <SelectTrigger className="font-mono w-full">
                  <SelectValue>
                    {selectedScenario.replace(/_/g, " ").toUpperCase()}
                  </SelectValue>
                </SelectTrigger>
                <SelectContent>
                  {SCENARIOS.map((scenario) => (
                    <SelectItem
                      key={scenario}
                      value={scenario}
                      className="font-mono cursor-pointer"
                    >
                      {scenario.replace(/_/g, " ").toUpperCase()}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <Button
              onClick={handleSimulate}
              disabled={loading}
              className="w-full bg-primary hover:bg-primary/90"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  SIMULATING...
                </>
              ) : (
                <>
                  <Play className="mr-2 h-4 w-4" />
                  RUN SIMULATION
                </>
              )}
            </Button>

            {result && (
              <div className="space-y-2 pt-4 border-t border-border">
                <div className="text-xs font-mono text-muted-foreground">
                  SIMULATION RESULTS
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Peak Risk:</span>
                    <span
                      className={`font-bold ${
                        result.peak_risk > 80
                          ? "text-destructive"
                          : "text-primary"
                      }`}
                    >
                      {result.peak_risk.toFixed(1)}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Impact:</span>
                    <span
                      className={`font-bold ${getImpactColor(
                        result.estimated_impact
                      )}`}
                    >
                      {result.estimated_impact}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Steps:</span>
                    <span className="font-bold text-primary">
                      {result.steps?.length || 0}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Simulation Steps */}
        <Card className="border-primary/30 lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-sm font-mono uppercase text-muted-foreground">
              Simulation Steps
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[500px]">
              {result && result.steps && result.steps.length > 0 ? (
                <div className="space-y-4">
                  {result.steps.map((step, idx) => (
                    <div
                      key={idx}
                      className="border border-primary/20 rounded-md p-4 bg-secondary/20 hover:bg-secondary/30 transition-colors"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-xs font-mono font-bold text-primary">
                            {idx + 1}
                          </div>
                          <div>
                            <div className="text-sm font-mono text-muted-foreground">
                              Tick #{step.tick}
                            </div>
                            <div className="text-xs text-muted-foreground">
                              Risk: {step.risk_score.toFixed(1)}/100
                            </div>
                          </div>
                        </div>
                        <div
                          className={`text-xs font-mono px-2 py-1 rounded ${
                            step.risk_score > 80
                              ? "bg-destructive/20 text-destructive"
                              : step.risk_score > 50
                              ? "bg-yellow-500/20 text-yellow-500"
                              : "bg-primary/20 text-primary"
                          }`}
                        >
                          {step.risk_score.toFixed(0)}
                        </div>
                      </div>
                      <p className="text-sm text-foreground mb-2">
                        {step.description}
                      </p>
                      <div className="text-xs text-muted-foreground">
                        Affected Wallets: {step.affected_wallets.length} (
                        {step.affected_wallets.slice(0, 3).join(", ")}
                        {step.affected_wallets.length > 3 ? "..." : ""})
                      </div>
                    </div>
                  ))}
                </div>
              ) : result && result.error ? (
                <div className="text-destructive text-sm">{result.error}</div>
              ) : (
                <div className="text-center text-muted-foreground py-12">
                  Select a scenario and click "RUN SIMULATION" to start
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      {/* AI Recommendation */}
      {result && result.aegis_recommendation && (
        <Card className="border-primary/30 mt-6">
          <CardHeader>
            <CardTitle className="text-sm font-mono uppercase text-muted-foreground flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" />
              AI Recommendation (AEGIS)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-secondary/20 border border-primary/20 rounded-md p-4">
              <p className="text-sm whitespace-pre-wrap">
                {result.aegis_recommendation}
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
