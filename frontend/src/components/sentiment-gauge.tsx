import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { cn } from "../lib/utils";

interface SentimentGaugeProps {
  sentimentScore?: number; // 0-100 (0 = Panic, 50 = Neutral, 100 = Greed)
  className?: string;
}

export function SentimentGauge({ sentimentScore = 50, className }: SentimentGaugeProps) {
  const [animatedScore, setAnimatedScore] = useState(sentimentScore);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const startScoreRef = useRef(sentimentScore);

  useEffect(() => {
    // Clear any existing animation
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    const startScore = animatedScore;
    startScoreRef.current = startScore;
    const scoreDiff = sentimentScore - startScore;

    if (Math.abs(scoreDiff) < 0.1) {
      setAnimatedScore(sentimentScore);
      return;
    }

    // Smooth animation to target score
    const duration = 1000;
    const steps = 30;
    const stepTime = duration / steps;
    let currentStep = 0;

    intervalRef.current = setInterval(() => {
      currentStep++;
      const progress = currentStep / steps;
      // Easing function for smooth animation
      const eased = 1 - Math.pow(1 - progress, 3);
      const newScore = startScore + scoreDiff * eased;
      setAnimatedScore(newScore);

      if (currentStep >= steps) {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
        setAnimatedScore(sentimentScore);
      }
    }, stepTime);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [sentimentScore]);

  // Convert 0-100 score to angle (0° = left/panic, 180° = right/greed)
  const angle = (animatedScore / 100) * 180 - 90; // -90° to 90°
  const radius = 120;
  const centerX = 150;
  const centerY = 150;

  // Calculate needle position
  const needleX = centerX + radius * Math.cos((angle * Math.PI) / 180);
  const needleY = centerY + radius * Math.sin((angle * Math.PI) / 180);

  const getSentimentLabel = (score: number): string => {
    if (score >= 75) return "EXTREME GREED";
    if (score >= 55) return "GREED";
    if (score >= 45) return "NEUTRAL";
    if (score >= 25) return "FEAR";
    return "EXTREME FEAR";
  };

  const getSentimentColor = (score: number): string => {
    if (score >= 75) return "text-green-500";
    if (score >= 55) return "text-green-400";
    if (score >= 45) return "text-yellow-500";
    if (score >= 25) return "text-orange-500";
    return "text-red-500";
  };

  return (
    <Card className={cn("border-gray-800 bg-black/40", className)}>
      <CardHeader>
        <CardTitle className="text-center text-lg font-mono uppercase text-gray-400">
          GLOBAL NETWORK EMOTION
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col items-center justify-center py-6">
          {/* Semi-circular gauge */}
          <div className="relative" style={{ width: 300, height: 160 }}>
            <svg
              width={300}
              height={160}
              className="overflow-visible"
              style={{ transform: "scale(1)" }}
            >
              {/* Background arc */}
              <defs>
                <linearGradient id="sentimentGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#ef4444" stopOpacity="0.8" />
                  <stop offset="50%" stopColor="#eab308" stopOpacity="0.8" />
                  <stop offset="100%" stopColor="#22c55e" stopOpacity="0.8" />
                </linearGradient>
              </defs>

              {/* Semi-circle arc */}
              <path
                d={`M 30 140 A 120 120 0 0 1 270 140`}
                fill="none"
                stroke="url(#sentimentGradient)"
                strokeWidth="20"
                strokeLinecap="round"
                className="drop-shadow-lg"
              />

              {/* Zone indicators */}
              <text
                x="40"
                y="145"
                className="text-xs font-mono fill-gray-500"
                fontSize="10"
              >
                PANIC
              </text>
              <text
                x="130"
                y="155"
                className="text-xs font-mono fill-gray-500"
                fontSize="10"
              >
                NEUTRAL
              </text>
              <text
                x="220"
                y="145"
                className="text-xs font-mono fill-gray-500"
                fontSize="10"
              >
                GREED
              </text>

              {/* Needle */}
              <line
                x1={centerX}
                y1={centerY}
                x2={needleX}
                y2={needleY}
                stroke="#00ff41"
                strokeWidth="3"
                strokeLinecap="round"
                className="transition-all duration-300 drop-shadow-[0_0_8px_rgba(0,255,65,0.6)]"
                style={{
                  filter: "drop-shadow(0 0 4px rgba(0, 255, 65, 0.8))",
                }}
              />

              {/* Center dot */}
              <circle
                cx={centerX}
                cy={centerY}
                r="8"
                fill="#00ff41"
                className="drop-shadow-[0_0_8px_rgba(0,255,65,0.8)]"
              />
            </svg>
          </div>

          {/* Score display */}
          <div className="mt-6 text-center">
            <div className="flex items-baseline justify-center gap-2">
              <span
                className={cn(
                  "text-5xl font-bold font-mono transition-colors duration-300",
                  getSentimentColor(animatedScore)
                )}
              >
                {Math.round(animatedScore)}
              </span>
              <span className="text-xl text-gray-500 font-mono">/100</span>
            </div>
            <div
              className={cn(
                "mt-2 text-lg font-bold font-mono uppercase transition-colors duration-300",
                getSentimentColor(animatedScore)
              )}
            >
              {getSentimentLabel(animatedScore)}
            </div>
            <div className="mt-3 text-xs font-mono text-gray-500">
              Market sentiment derived from on-chain activity & social signals
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

