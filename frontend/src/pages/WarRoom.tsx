import { useState } from "react";
import { SimulationCard } from "../components/simulation-card";
import { ActionNotification } from "../components/action-notification";
import { TrendingDown, Skull, Zap } from "lucide-react";
import { toast } from "sonner";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card";

export function WarRoom() {
  const [activeScenario, setActiveScenario] = useState<string | null>(null);
  const [showNotification, setShowNotification] = useState(false);
  const [notificationData, setNotificationData] = useState<{
    threatType: string;
    riskScore: number;
  } | null>(null);

  const webhookUrl =
    "https://qubicaegis.app.n8n.cloud/webhook/b4662347-9dd7-4934-8eab-33bbcee20ddc";

  const handleSimulation = async (scenarioType: string) => {
    if (activeScenario !== null) {
      return;
    }

    setActiveScenario(scenarioType);

    const scenarioNames = {
      WHALE: "Whale Dump",
      RUG: "Rug Pull",
      FLASH: "Flash Loan Attack",
    };

    const scenarioTypes = {
      WHALE: "WHALE_DUMP",
      RUG: "RUG_PULL_INITIATED",
      FLASH: "FLASH_LOAN_ATTACK",
    };

    const riskScores = {
      WHALE: 92,
      RUG: 99,
      FLASH: 95,
    };

    const scenarioName =
      scenarioNames[scenarioType as keyof typeof scenarioNames] || "threat";
    const threatType =
      scenarioTypes[scenarioType as keyof typeof scenarioTypes] || "UNKNOWN";
    const riskScore = riskScores[scenarioType as keyof typeof riskScores] || 90;
    const toastId = `warroom-${scenarioType}`;

    toast.loading(`Injecting ${scenarioName} into network stream...`, {
      id: toastId,
    });

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
            scenario_type: scenarioType,
            message: `QUBIC AEGIS Alert: ${scenarioName} detected`,
          }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        // Show the big notification
        setNotificationData({ threatType, riskScore });
        setShowNotification(true);

        toast.success(
          `✅ ${scenarioName} injected! Attack in network stream.`,
          {
            id: toastId,
            duration: 4000,
            description:
              "ATTACK INJECTED INTO NETWORK STREAM - Monitoring active",
          }
        );
      } else {
        toast.error(`❌ Injection failed: ${data.detail || "Unknown error"}`, {
          id: toastId,
          duration: 4000,
        });
      }
    } catch (error) {
      toast.error(`❌ Error: ${error}`, {
        id: toastId,
        duration: 4000,
      });
    } finally {
      setTimeout(() => {
        setActiveScenario(null);
      }, 3000);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 bg-[#050505]">
      {/* Action Notification */}
      {showNotification && notificationData && (
        <ActionNotification
          isVisible={showNotification}
          threatType={notificationData.threatType}
          riskScore={notificationData.riskScore}
          onClose={() => {
            setShowNotification(false);
            setNotificationData(null);
          }}
        />
      )}

      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight font-mono text-[#00ff41] mb-2">
            WAR ROOM
          </h1>
          <p className="text-sm text-gray-400 font-mono">
            Attack Simulation & Network Stress Testing
          </p>
        </div>

        {activeScenario && (
          <Card className="mb-6 border-2 border-yellow-500 bg-yellow-900/20">
            <CardContent className="pt-6">
              <div className="text-center font-mono">
                <div className="text-yellow-500 text-lg font-bold animate-pulse">
                  ATTACK INJECTED INTO NETWORK STREAM
                </div>
                <div className="text-xs text-gray-400 mt-2">
                  Monitoring transaction flow for anomaly detection...
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid gap-6 md:grid-cols-3">
          <SimulationCard
            title="WHALE DUMP"
            icon={TrendingDown}
            description="Simulate a massive sell-off by a whale wallet. Detects market manipulation patterns and liquidity impact."
            color="yellow"
            onClick={() => handleSimulation("WHALE")}
            disabled={activeScenario !== null}
            loading={activeScenario === "WHALE"}
          />

          <SimulationCard
            title="RUG PULL"
            icon={Skull}
            description="Simulate a rug pull scenario with liquidity removal. Tests critical threat detection capabilities."
            color="red"
            onClick={() => handleSimulation("RUG")}
            disabled={activeScenario !== null}
            loading={activeScenario === "RUG"}
          />

          <SimulationCard
            title="FLASH LOAN"
            icon={Zap}
            description="Simulate a flash loan exploit attack. Detects abnormal arbitrage and re-entrancy patterns."
            color="purple"
            onClick={() => handleSimulation("FLASH")}
            disabled={activeScenario !== null}
            loading={activeScenario === "FLASH"}
          />
        </div>

        <Card className="mt-8 border-gray-800 bg-black/40">
          <CardHeader>
            <CardTitle className="text-sm font-mono uppercase text-gray-400">
              SIMULATION INSTRUCTIONS
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm font-mono text-gray-400">
              <p>
                1. Select an attack scenario to inject into the network stream
              </p>
              <p>2. The attack will be simulated and analyzed in real-time</p>
              <p>3. Monitor the LIVE MONITOR page to see detection in action</p>
              <p>4. Check Discord for automated alerts via n8n integration</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
