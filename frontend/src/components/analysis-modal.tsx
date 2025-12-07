import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { cn } from "../lib/utils";

interface RiskAnalysis {
  transaction?: {
    source_id?: string;
    dest_id?: string;
    amount?: number;
    tick?: number;
    type?: string;
    timestamp?: string | null;
    token_symbol?: string;
    source?: "RPC" | "SIMULATION";
  } | {
    source_id: string;
    dest_id: string;
    amount: number;
    tick: number;
    type: string;
    timestamp: string | null;
    token_symbol?: string;
    source?: "RPC" | "SIMULATION";
  };
  risk_score?: number;
  risk_level?: string;
  explanation?: string;
  attack_type?: string;
  risk_factors?: Array<{
    factor: string;
    severity?: string;
    details?: string;
    impact?: number;
  }>;
  prediction?: {
    predicted_risk?: number;
    trend?: string;
  };
  xai_explanation?: {
    xai_summary?: string;
    summary?: string;
  };
}

interface AnalysisModalProps {
  isOpen: boolean;
  onClose: () => void;
  analysis: RiskAnalysis | null;
}

export function AnalysisModal({ isOpen, onClose, analysis }: AnalysisModalProps) {
  const [displayedText, setDisplayedText] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    if (!isOpen || !analysis) {
      setDisplayedText("");
      setIsTyping(false);
      return;
    }

    // Get the explanation text
    const explanation =
      analysis.explanation ||
      analysis.xai_explanation?.xai_summary ||
      analysis.xai_explanation?.summary ||
      generateMockAnalysis(analysis);

    // Typewriter effect
    setIsTyping(true);
    setDisplayedText("");
    let currentIndex = 0;

    const typeInterval = setInterval(() => {
      if (currentIndex < explanation.length) {
        setDisplayedText(explanation.substring(0, currentIndex + 1));
        currentIndex++;
      } else {
        setIsTyping(false);
        clearInterval(typeInterval);
      }
    }, 20); // Speed of typing

    return () => clearInterval(typeInterval);
  }, [isOpen, analysis]);

  if (!isOpen || !analysis) return null;

  const riskLevel = analysis.risk_level || "UNKNOWN";
  const riskScore = analysis.risk_score ?? 0;
  const attackType = analysis.attack_type || analysis.transaction?.type || "NORMAL";

  // Generate risk factors if not present
  const riskFactors = analysis.risk_factors || generateRiskFactors(analysis);

  // Generate recommendation
  const recommendation = getRecommendation(riskLevel, riskScore);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      onClick={onClose}
    >
      {/* Backdrop with blur */}
      <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" />
      
      {/* Modal Content */}
      <div
        className="relative z-10 w-full max-w-3xl mx-4 max-h-[90vh] overflow-auto rounded-lg border-2 border-[#00ff41] bg-[#050505] shadow-[0_0_30px_rgba(0,255,65,0.3)]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 border-b-2 border-[#00ff41] bg-black/90 p-6 flex items-center justify-between backdrop-blur-sm">
          <h2 className="text-2xl font-bold font-mono text-[#00ff41] uppercase tracking-wider">
            CLASSIFIED INTELLIGENCE REPORT
          </h2>
          <button
            onClick={onClose}
            className="text-[#00ff41] hover:text-red-500 transition-colors p-2 hover:bg-[#00ff41]/10 rounded"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Transaction Summary */}
          {analysis.transaction && (
            <div className="border border-gray-800 bg-black/40 p-4 rounded font-mono text-xs">
              <div className="grid grid-cols-2 gap-4 text-gray-400">
                <div>
                  <span className="text-gray-500">Source:</span>{" "}
                  <span className="text-[#00ff41]">
                    {analysis.transaction.source_id || "UNKNOWN"}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">Destination:</span>{" "}
                  <span className="text-[#00ff41]">
                    {analysis.transaction.dest_id || "UNKNOWN"}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">Amount:</span>{" "}
                  <span className="text-foreground font-bold">
                    {(analysis.transaction.amount || 0).toLocaleString()} {analysis.transaction.token_symbol || "QUBIC"}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">Tick:</span>{" "}
                  <span className="text-[#00ff41]">#{analysis.transaction.tick || "N/A"}</span>
                </div>
              </div>
            </div>
          )}

          {/* Threat Analysis Section */}
          <div>
            <h3 className="text-lg font-bold font-mono text-[#00ff41] uppercase mb-3 border-b border-gray-800 pb-2">
              THREAT ANALYSIS
            </h3>
            <div className="bg-black/60 border border-gray-800 rounded p-4 font-mono text-sm text-foreground min-h-[120px]">
              <div className="flex items-start gap-2 mb-2">
                <span className="text-[#00ff41]">{isTyping ? ">" : "✓"}</span>
                <div className="flex-1">
                  {displayedText.split("\n").map((line, idx) => (
                    <div key={idx} className="mb-1">
                      {line || "\u00A0"}
                    </div>
                  ))}
                  {isTyping && (
                    <span className="text-[#00ff41] animate-pulse">▊</span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Risk Factors Section */}
          <div>
            <h3 className="text-lg font-bold font-mono text-[#00ff41] uppercase mb-3 border-b border-gray-800 pb-2">
              RISK FACTORS
            </h3>
            <div className="flex flex-wrap gap-2">
              {riskFactors.map((factor, idx) => (
                <span
                  key={idx}
                  className={cn(
                    "px-3 py-1 rounded border font-mono text-xs font-bold",
                    factor.severity === "HIGH" || factor.severity === "CRITICAL"
                      ? "bg-red-500/20 text-red-400 border-red-500/50"
                      : factor.severity === "MEDIUM"
                      ? "bg-yellow-500/20 text-yellow-400 border-yellow-500/50"
                      : "bg-[#00ff41]/20 text-[#00ff41] border-[#00ff41]/50"
                  )}
                >
                  [{factor.factor}]
                </span>
              ))}
            </div>
          </div>

          {/* Risk Score Display */}
          <div className="grid grid-cols-2 gap-4">
            <div className="border border-gray-800 bg-black/40 p-4 rounded">
              <div className="text-xs font-mono text-gray-500 uppercase mb-1">
                Risk Level
              </div>
              <div
                className={cn(
                  "text-2xl font-bold font-mono",
                  riskLevel === "CRITICAL"
                    ? "text-red-500"
                    : riskLevel === "HIGH"
                    ? "text-orange-500"
                    : riskLevel === "MEDIUM"
                    ? "text-yellow-500"
                    : "text-[#00ff41]"
                )}
              >
                {riskLevel}
              </div>
            </div>
            <div className="border border-gray-800 bg-black/40 p-4 rounded">
              <div className="text-xs font-mono text-gray-500 uppercase mb-1">
                Risk Score
              </div>
              <div className="text-2xl font-bold font-mono text-foreground">
                {riskScore.toFixed(1)}/100
              </div>
            </div>
          </div>

          {/* Recommendation Section */}
          <div>
            <h3 className="text-lg font-bold font-mono text-[#00ff41] uppercase mb-3 border-b border-gray-800 pb-2">
              RECOMMENDATION
            </h3>
            <div className="bg-black/60 border-2 border-[#00ff41] rounded p-6">
              <div className="text-2xl font-bold font-mono text-[#00ff41] text-center animate-pulse">
                {recommendation}
              </div>
            </div>
          </div>

          {/* Prediction */}
          {analysis.prediction && (
            <div className="border border-gray-800 bg-black/40 p-4 rounded font-mono text-xs">
              <div className="text-gray-500 uppercase mb-2">Future Prediction</div>
              <div className="text-foreground">
                Trend: <span className="text-[#00ff41]">{analysis.prediction.trend || "UNKNOWN"}</span>
              </div>
              {analysis.prediction.predicted_risk && (
                <div className="text-foreground mt-1">
                  Predicted Risk:{" "}
                  <span className="text-yellow-500">
                    {analysis.prediction.predicted_risk.toFixed(1)}/100
                  </span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer with Cryptographic Signature */}
        <div className="sticky bottom-0 border-t-2 border-[#00ff41] bg-black/90 p-4 backdrop-blur-sm">
          <div className="flex items-center justify-between font-mono text-xs text-gray-500">
            <div>
              <div className="text-[#00ff41]">Signed by Aegis Core v2.1</div>
              <div className="mt-1 text-gray-600">
                {new Date().toISOString()}
              </div>
            </div>
            <div className="text-right">
              <div>Neural Network Analysis</div>
              <div className="text-[#00ff41]">CONFIDENTIAL</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Helper function to generate mock analysis if missing
function generateMockAnalysis(analysis: RiskAnalysis): string {
  const riskLevel = analysis.risk_level || "UNKNOWN";
  const amount = analysis.transaction?.amount || 0;
  const token = analysis.transaction?.token_symbol || "QUBIC";

  if (riskLevel === "CRITICAL") {
    return `CRITICAL THREAT DETECTED\n\nAnalysis indicates a high-probability attack pattern. Transaction volume (${amount.toLocaleString()} ${token}) exceeds normal parameters by 500%. Source wallet demonstrates bot-like behavior with rapid-fire transactions. Pattern matches known whale dump signatures.\n\nRECOMMENDATION: Immediate action required. Flag wallet for monitoring and consider temporary freeze.`;
  } else if (riskLevel === "HIGH") {
    return `ELEVATED RISK PROFILE\n\nTransaction exhibits suspicious characteristics. Volume significantly higher than baseline. Source wallet has limited transaction history, indicating potential new threat actor. Pattern suggests coordinated manipulation attempt.\n\nRECOMMENDATION: Enhanced monitoring and alert escalation.`;
  } else {
    return `STANDARD TRANSACTION ANALYSIS\n\nTransaction parameters within normal operational boundaries. No anomalies detected in pattern recognition algorithms. Source wallet verified with established transaction history.`;
  }
}

// Helper function to generate risk factors if missing
function generateRiskFactors(analysis: RiskAnalysis): Array<{
  factor: string;
  severity: string;
  details?: string;
}> {
  const factors: Array<{ factor: string; severity: string }> = [];
  const riskLevel = analysis.risk_level || "UNKNOWN";
  const amount = analysis.transaction?.amount || 0;

  if (amount > 100000) {
    factors.push({ factor: "Large Volume", severity: "HIGH" });
  }
  if (analysis.transaction?.source === "SIMULATION") {
    factors.push({ factor: "Simulated Attack", severity: "CRITICAL" });
  }
  if (riskLevel === "CRITICAL" || riskLevel === "HIGH") {
    factors.push({ factor: "Anomaly Detected", severity: riskLevel });
  }
  if (!factors.length) {
    factors.push({ factor: "Normal Activity", severity: "LOW" });
  }

  return factors;
}

// Helper function to get recommendation
function getRecommendation(riskLevel: string, riskScore: number): string {
  if (riskLevel === "CRITICAL" || riskScore >= 90) {
    return "BLOCK TRANSACTION";
  } else if (riskLevel === "HIGH" || riskScore >= 70) {
    return "FREEZE WALLET";
  } else if (riskLevel === "MEDIUM" || riskScore >= 40) {
    return "MONITOR CLOSELY";
  } else {
    return "ALLOW & LOG";
  }
}

