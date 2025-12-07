import { cn } from "../lib/utils";

interface DefconBadgeProps {
  level: number;
  className?: string;
  size?: "sm" | "md" | "lg";
}

export function DefconBadge({
  level,
  className,
  size = "md",
}: DefconBadgeProps) {
  const getColor = (defconLevel: number) => {
    if (defconLevel <= 1) return "text-red-500 border-red-500 bg-red-500/10";
    if (defconLevel === 2)
      return "text-orange-500 border-orange-500 bg-orange-500/10";
    if (defconLevel === 3)
      return "text-yellow-500 border-yellow-500 bg-yellow-500/10";
    if (defconLevel === 4)
      return "text-blue-500 border-blue-500 bg-blue-500/10";
    return "text-green-500 border-green-500 bg-green-500/10";
  };

  const getGlow = (defconLevel: number) => {
    if (defconLevel <= 2) return "gentle-pulse";
    if (defconLevel === 3) return "";
    return "";
  };

  const sizeClasses = {
    sm: "text-xs px-2 py-1",
    md: "text-sm px-3 py-1.5",
    lg: "text-base px-4 py-2",
  };

  const isCritical = level <= 2;

  return (
    <div
      className={cn(
        "inline-flex items-center gap-2 rounded border-2 font-mono font-bold uppercase transition-all",
        getColor(level),
        sizeClasses[size],
        isCritical && getGlow(level),
        isCritical && "shadow-lg shadow-red-500/50",
        className
      )}
    >
      <span className={cn(isCritical && "gentle-pulse")}>DEFCON</span>
      <span>{level}</span>
    </div>
  );
}
