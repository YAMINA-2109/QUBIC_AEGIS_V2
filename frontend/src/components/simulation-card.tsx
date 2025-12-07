import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import type { LucideIcon } from "lucide-react";
import { cn } from "../lib/utils";

interface SimulationCardProps {
  title: string;
  icon: LucideIcon;
  description: string;
  color: "yellow" | "red" | "purple";
  onClick: () => void;
  disabled?: boolean;
  loading?: boolean;
}

export function SimulationCard({
  title,
  icon: Icon,
  description,
  color,
  onClick,
  disabled = false,
  loading = false,
}: SimulationCardProps) {
  const colorClasses = {
    yellow: {
      border: "border-yellow-500",
      bg: "bg-yellow-900/20 hover:bg-yellow-900/40",
      text: "text-yellow-500",
      glow: "hover:shadow-yellow-500/50",
    },
    red: {
      border: "border-red-500",
      bg: "bg-red-900/20 hover:bg-red-900/40",
      text: "text-red-500",
      glow: "hover:shadow-red-500/50",
    },
    purple: {
      border: "border-purple-500",
      bg: "bg-purple-900/20 hover:bg-purple-900/40",
      text: "text-purple-500",
      glow: "hover:shadow-purple-500/50",
    },
  };

  const classes = colorClasses[color];

  return (
    <Card
      className={cn(
        "cursor-pointer transition-all border-2",
        classes.border,
        classes.bg,
        !disabled && "hover:scale-105 hover:shadow-xl",
        classes.glow,
        disabled && "opacity-50 cursor-not-allowed"
      )}
      onClick={disabled ? undefined : onClick}
    >
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle
            className={cn("text-xl font-mono uppercase", classes.text)}
          >
            {title}
          </CardTitle>
          <Icon className={cn("h-8 w-8", classes.text)} />
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground font-mono">{description}</p>
        {loading && (
          <div className="mt-4 text-xs font-mono text-primary animate-pulse">
            INJECTING INTO NETWORK STREAM...
          </div>
        )}
      </CardContent>
    </Card>
  );
}
