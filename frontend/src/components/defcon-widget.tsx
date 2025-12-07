import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { useState, useEffect } from "react";
import { AlertTriangle, Shield } from "lucide-react";
import { cn } from "../lib/utils";

interface DEFCONStatus {
  defcon_level: number;
  alert_threshold: number;
  attacks_last_minute: number;
  status: string;
}

export function DEFCONWidget() {
  const [defconStatus, setDefconStatus] = useState<DEFCONStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDEFCON = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/defcon-status");
        if (response.ok) {
          const data = await response.json();
          setDefconStatus(data);
        }
      } catch (error) {
        console.error("Error fetching DEFCON status:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDEFCON();
    const interval = setInterval(fetchDEFCON, 3000); // Update every 3s
    return () => clearInterval(interval);
  }, []);

  if (loading || !defconStatus) {
    return null;
  }

  const getDEFCONColor = (level: number) => {
    if (level <= 2) return "text-destructive border-destructive";
    if (level <= 3) return "text-orange-500 border-orange-500";
    return "text-primary border-primary";
  };

  const getDEFCONGlow = (level: number) => {
    if (level <= 2) return "cyber-glow-red";
    return "";
  };

  const isCritical = defconStatus.defcon_level <= 2;

  return (
    <Card
      className={cn(
        "border-2 transition-all",
        isCritical
          ? `${getDEFCONColor(defconStatus.defcon_level)} ${getDEFCONGlow(
              defconStatus.defcon_level
            )}`
          : "border-primary/30"
      )}
    >
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-mono uppercase text-muted-foreground flex items-center gap-2">
          <Shield className="h-4 w-4" />
          DEFCON STATUS
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div>
            <div
              className={cn(
                "text-4xl font-bold font-mono",
                getDEFCONColor(defconStatus.defcon_level).split(" ")[0]
              )}
            >
              DEFCON {defconStatus.defcon_level}
            </div>
            <div className="text-xs text-muted-foreground mt-1 font-mono">
              Alert Threshold: {defconStatus.alert_threshold.toFixed(0)}
            </div>
          </div>
          <div className="text-right">
            {defconStatus.attacks_last_minute > 0 && (
              <>
                <div className="text-2xl font-bold font-mono text-destructive">
                  {defconStatus.attacks_last_minute}
                </div>
                <div className="text-xs text-muted-foreground font-mono">
                  attacks/min
                </div>
              </>
            )}
          </div>
        </div>
        {isCritical && (
          <div className="mt-3 pt-3 border-t border-destructive/30 flex items-center gap-2 text-destructive text-xs font-mono">
            <AlertTriangle className="h-3 w-3" />
            {defconStatus.status}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
