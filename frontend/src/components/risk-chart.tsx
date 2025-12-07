import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { apiUrl } from "../lib/api";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

interface RiskHistoryData {
  time: string;
  risk: number;
}

interface RiskChartProps {
  data: RiskHistoryData[];
}

export function RiskChart({ data }: RiskChartProps) {
  const [prediction, setPrediction] = useState<{
    forecast: number[];
    predicted_risk: number;
  } | null>(null);

  useEffect(() => {
    const fetchPrediction = async () => {
      try {
        const response = await fetch(apiUrl("api/predict?horizon=short_term"));
        const predData = await response.json();
        setPrediction(predData);
      } catch (error) {
        console.error("Error fetching prediction:", error);
      }
    };

    fetchPrediction();
    const interval = setInterval(fetchPrediction, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  // Combine historical data with predictions
  const chartData = [...data];

  // Add prediction points (forecast starts from last data point)
  if (prediction && chartData.length > 0) {
    const lastTime = chartData[chartData.length - 1].time;
    const forecastPoints = prediction.forecast?.slice(0, 20) || []; // Limit to 20 points

    forecastPoints.forEach((predictedRisk: number, idx: number) => {
      // Generate future timestamps (assuming 2s intervals)
      const minutes = Math.floor((idx * 2) / 60);
      const seconds = (idx * 2) % 60;
      const [hours, mins] = lastTime.split(":").map(Number);
      const newMins = mins + minutes;
      const newHours = newMins >= 60 ? hours + 1 : hours;
      const futureTime = `${String(newHours % 24).padStart(2, "0")}:${String(
        newMins % 60
      ).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;

      chartData.push({
        time: futureTime,
        risk: predictedRisk,
      });
    });
  }

  const currentIndex = data.length - 1;
  const predictionStartIndex = data.length;

  return (
    <Card className="border-primary/30">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-mono uppercase text-muted-foreground">
            Risk Over Time with AI Prediction
          </CardTitle>
          {prediction && (
            <div className="text-xs text-muted-foreground">
              Predicted: {prediction.predicted_risk.toFixed(1)}
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="rgba(255,255,255,0.1)"
            />
            <XAxis
              dataKey="time"
              stroke="rgba(255,255,255,0.5)"
              style={{ fontSize: "12px", fontFamily: "monospace" }}
            />
            <YAxis
              stroke="rgba(255,255,255,0.5)"
              style={{ fontSize: "12px", fontFamily: "monospace" }}
              domain={[0, 100]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "rgba(0,0,0,0.9)",
                border: "1px solid rgba(0,255,100,0.3)",
                borderRadius: "4px",
                fontFamily: "monospace",
              }}
              labelStyle={{ color: "rgba(0,255,100,1)" }}
            />
            {/* Historical data line */}
            <Line
              type="monotone"
              dataKey="risk"
              stroke="rgba(0,255,100,1)"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6, fill: "rgba(0,255,100,1)" }}
              data={data}
            />
            {/* Prediction line (dashed, red) */}
            {prediction && chartData.length > predictionStartIndex && (
              <Line
                type="monotone"
                dataKey="risk"
                stroke="rgba(255,50,50,0.8)"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                data={chartData.slice(predictionStartIndex)}
              />
            )}
            {/* Reference line at current time */}
            {currentIndex >= 0 && (
              <ReferenceLine
                x={chartData[currentIndex]?.time}
                stroke="rgba(255,255,255,0.5)"
                strokeDasharray="3 3"
                label={{
                  value: "Now",
                  position: "top",
                  fill: "rgba(255,255,255,0.7)",
                }}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
        <div className="mt-4 flex gap-4 text-xs text-muted-foreground">
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 bg-neon-green"></div>
            <span>Historical Risk</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 border-t-2 border-dashed border-red-500"></div>
            <span>AI Prediction</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
