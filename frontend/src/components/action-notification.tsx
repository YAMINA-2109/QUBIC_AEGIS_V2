import { useEffect, useState } from "react";
import { Zap, Shield, CheckCircle2 } from "lucide-react";
import { cn } from "../lib/utils";

interface ActionNotificationProps {
  isVisible: boolean;
  threatType: string;
  riskScore: number;
  onClose: () => void;
}

export function ActionNotification({
  isVisible,
  threatType,
  riskScore,
  onClose,
}: ActionNotificationProps) {
  const [phase, setPhase] = useState<"detected" | "blocking" | "executed">(
    "detected"
  );

  useEffect(() => {
    if (!isVisible) {
      setPhase("detected");
      return;
    }

    // Phase 1: Threat Detected (0-1s)
    const timer1 = setTimeout(() => {
      setPhase("blocking");
    }, 1000);

    // Phase 2: Blocking (1-3s)
    const timer2 = setTimeout(() => {
      setPhase("executed");
    }, 3000);

    // Phase 3: Auto-close after 5s total
    const timer3 = setTimeout(() => {
      onClose();
    }, 5000);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, [isVisible, onClose]);

  if (!isVisible) return null;

  const getThreatLabel = (type: string): string => {
    const labels: Record<string, string> = {
      WHALE_DUMP: "WHALE DUMP",
      RUG_PULL_INITIATED: "RUG PULL",
      FLASH_LOAN_ATTACK: "FLASH LOAN ATTACK",
    };
    return labels[type] || type;
  };

  return (
    <div className="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 animate-in fade-in slide-in-from-top-5 duration-300">
      <div
        className={cn(
          "relative w-[600px] rounded-lg border-2 bg-black/95 backdrop-blur-md shadow-2xl p-6 font-mono",
          phase === "detected"
            ? "border-red-500 shadow-red-500/50"
            : phase === "blocking"
            ? "border-yellow-500 shadow-yellow-500/50 animate-pulse"
            : "border-green-500 shadow-green-500/50"
        )}
      >
        {/* Header */}
        <div className="flex items-center gap-3 mb-4">
          {phase === "detected" && (
            <Zap className="h-8 w-8 text-red-500 animate-pulse" />
          )}
          {phase === "blocking" && (
            <Shield className="h-8 w-8 text-yellow-500 animate-spin" />
          )}
          {phase === "executed" && (
            <CheckCircle2 className="h-8 w-8 text-green-500" />
          )}
          <div>
            <div
              className={cn(
                "text-xl font-bold uppercase",
                phase === "detected"
                  ? "text-red-500"
                  : phase === "blocking"
                  ? "text-yellow-500"
                  : "text-green-500"
              )}
            >
              {phase === "detected" && "THREAT DETECTED"}
              {phase === "blocking" && "AI DECISION"}
              {phase === "executed" && "ACTION EXECUTED"}
            </div>
            <div className="text-xs text-gray-400">
              {phase === "detected" && getThreatLabel(threatType)}
              {phase === "blocking" && "BLOCKING TRANSACTION..."}
              {phase === "executed" && "via EasyConnect"}
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="space-y-2">
          {phase === "detected" && (
            <>
              <div className="text-sm text-gray-300">
                Threat Type:{" "}
                <span className="text-red-400 font-bold">
                  {getThreatLabel(threatType)}
                </span>
              </div>
              <div className="text-sm text-gray-300">
                Risk Score:{" "}
                <span className="text-red-400 font-bold">{riskScore}/100</span>
              </div>
            </>
          )}

          {phase === "blocking" && (
            <div className="text-lg text-yellow-400 font-bold animate-pulse">
              AI DECISION: BLOCKING TRANSACTION...
            </div>
          )}

          {phase === "executed" && (
            <div className="text-lg text-green-400 font-bold">
              ACTION EXECUTED via EasyConnect
            </div>
          )}
        </div>

        {/* Progress Bar */}
        <div className="mt-4 h-1 bg-gray-800 rounded-full overflow-hidden">
          <div
            className={cn(
              "h-full transition-all duration-500",
              phase === "detected"
                ? "w-1/3 bg-red-500"
                : phase === "blocking"
                ? "w-2/3 bg-yellow-500"
                : "w-full bg-green-500"
            )}
          />
        </div>
      </div>
    </div>
  );
}
