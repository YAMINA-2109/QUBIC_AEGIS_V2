import { Badge } from "./ui/badge";
import { useState, useEffect } from "react";
import { cn } from "../lib/utils";

interface HeaderProps {
  isConnected: boolean;
  defconStatus?: DEFCONStatus | null;
  isUnderAttack?: boolean;
}

interface DEFCONStatus {
  defcon_level: number;
  alert_threshold: number;
  attacks_last_minute: number;
  status: string;
}

export function Header({
  isConnected,
  defconStatus: propDefconStatus,
  isUnderAttack,
}: HeaderProps) {
  const [defconStatus, setDefconStatus] = useState<DEFCONStatus | null>(
    propDefconStatus || null
  );

  useEffect(() => {
    if (propDefconStatus) {
      setDefconStatus(propDefconStatus);
      return;
    }

    const fetchDEFCON = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/defcon-status");
        if (response.ok) {
          const data = await response.json();
          setDefconStatus(data);
        }
      } catch (error) {
        // Silently fail if DEFCON endpoint not available
      }
    };

    fetchDEFCON();
    const interval = setInterval(fetchDEFCON, 5000); // Update every 5s
    return () => clearInterval(interval);
  }, [propDefconStatus]);

  const getDEFCONColor = (level?: number) => {
    if (!level) return "text-muted-foreground";
    if (level <= 2) return "text-destructive";
    if (level <= 3) return "text-orange-500";
    return "text-primary";
  };

  return (
    <header className="flex h-16 items-center justify-between border-b border-gray-800 bg-[#0a0a0a] px-6">
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-bold tracking-wider text-foreground font-mono">
          QUBIC AEGIS - NEURAL DEFENSE SYSTEM
        </h1>
      </div>

      <div className="flex items-center gap-4">
        {/* DEFCON Status */}
        {defconStatus && (
          <div className="flex items-center gap-2 border-r border-border pr-4">
            <Badge
              className={`${getDEFCONColor(
                defconStatus.defcon_level
              )} bg-transparent border ${
                defconStatus.defcon_level <= 2
                  ? "border-destructive"
                  : "border-primary/30"
              } px-2 py-1 font-mono text-xs`}
            >
              DEFCON {defconStatus.defcon_level}
            </Badge>
            {defconStatus.attacks_last_minute > 0 && (
              <span className="text-xs font-mono text-muted-foreground">
                {defconStatus.attacks_last_minute} attacks/min
              </span>
            )}
          </div>
        )}

        <Badge
          className={cn(
            "px-3 py-1 border",
            isUnderAttack
              ? "bg-red-500/20 text-red-500 border-red-500 gentle-pulse"
              : isConnected
              ? "bg-primary text-primary-foreground border-primary"
              : "bg-gray-500 text-gray-300 border-gray-500"
          )}
        >
          <span
            className={cn(
              "mr-2 inline-block h-2 w-2 rounded-full",
              isUnderAttack
                ? "bg-red-500 gentle-pulse"
                : isConnected
                ? "bg-primary-foreground gentle-pulse"
                : "bg-red-500"
            )}
          />
          {isUnderAttack
            ? "UNDER ATTACK"
            : isConnected
            ? "ONLINE"
            : "OFFLINE"}
        </Badge>
        <div className="text-xs font-mono text-muted-foreground">
          {new Date().toLocaleTimeString("en-US", { hour12: false })}
        </div>
      </div>
    </header>
  );
}
