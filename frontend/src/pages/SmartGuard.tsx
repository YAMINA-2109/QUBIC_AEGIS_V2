import { useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import {
  Shield,
  Loader2,
  Code,
  FileText,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";
import { toast } from "sonner";
import { MarkdownRenderer } from "../components/markdown-renderer";
import { MermaidDiagram } from "../components/mermaid-diagram";
import { ScrollArea } from "../components/ui/scroll-area";

interface AuditResult {
  commented?: string;
  semantic_report?: string;
  strict_validation_report?: string;
  audit_report?: string;
  functional_spec?: string;
  flow_diagram?: string;
  detailed_doc?: string;
  business_summary?: string;
  test_plan?: string;
  simulation_result?: string;
  qubic_logs?: string;
  compilation_success?: boolean;
  status: string;
  error?: string;
  message?: string;
}

const STEPS = [
  { id: 1, name: "Parse", label: "Parsing C++" },
  { id: 2, name: "Comment", label: "Code Comments" },
  { id: 3, name: "Review", label: "Review & Validation" },
  { id: 4, name: "Semantic", label: "Semantic Analysis" },
  { id: 5, name: "Audit", label: "Security Audit" },
  { id: 6, name: "Spec", label: "Functional Spec" },
  { id: 7, name: "Diagram", label: "Flow Diagram" },
  { id: 8, name: "Docs", label: "Documentation" },
  { id: 9, name: "Test", label: "Test Plan" },
  { id: 10, name: "Simulation", label: "Simulation" },
  { id: 11, name: "Compile", label: "Compilation" },
  { id: 12, name: "Export", label: "Export Report" },
];

export function SmartGuard() {
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("english");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AuditResult | null>(null);
  const [activeStep, setActiveStep] = useState(0);
  const [selectedTab, setSelectedTab] = useState<string | null>(null);

  const handleAudit = async () => {
    if (!code.trim()) {
      toast.error("Please enter C++ code to audit");
      return;
    }

    setLoading(true);
    setResult(null);
    setActiveStep(0);
    setSelectedTab(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/smart-guard/audit",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            code: code.trim(),
            language: language,
          }),
        }
      );

      const data: AuditResult = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.message || "Audit failed");
      }

      if (data.status === "error") {
        throw new Error(data.error || data.message || "Audit failed");
      }

      setResult(data);

      // Simulate progress through steps
      let step = 0;
      const progressInterval = setInterval(() => {
        step += 1;
        setActiveStep(step);
        if (step >= STEPS.length) {
          clearInterval(progressInterval);
          setSelectedTab("audit");
          toast.success("Audit Complete! Full report generated.");
        }
      }, 500);

      return () => clearInterval(progressInterval);
    } catch (error) {
      console.error("Audit error:", error);
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";
      toast.error(`Audit failed: ${errorMessage}`);
      setResult({
        status: "error",
        error: errorMessage,
      });
    } finally {
      setLoading(false);
    }
  };

  const getResultField = (key: keyof AuditResult): string => {
    if (!result || result.status === "error") {
      return "";
    }
    const value = result[key];
    if (typeof value === "string") {
      return value;
    }
    return "";
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 bg-[#050505]">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight font-mono text-[#00ff41] mb-2 flex items-center gap-3">
            <Shield className="h-8 w-8" />
            SMARTGUARD
          </h1>
          <p className="text-sm text-gray-400 font-mono">
            AI-Powered C++ Smart Contract Auditing for Nostromo
          </p>
        </div>

        {/* Code Editor - Top Section (Collapsible when results are shown) */}
        <Card
          className={`border-gray-800 bg-black/40 mb-6 transition-all ${
            result && result.status === "success"
              ? "max-h-[300px] overflow-hidden"
              : ""
          }`}
        >
          <CardHeader>
            <CardTitle className="text-sm font-mono uppercase text-gray-400 flex items-center gap-2">
              <Code className="h-4 w-4" />
              C++ SMART CONTRACT CODE
              {result && result.status === "success" && (
                <span className="ml-auto text-xs text-gray-500">
                  (Minimized - Results below)
                </span>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-4">
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="px-3 py-2 bg-black/60 border border-gray-800 rounded text-sm font-mono text-[#00ff41] focus:border-[#00ff41] focus:outline-none"
              >
                <option value="english">English</option>
                <option value="french">French</option>
              </select>
            </div>
            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder={`extern "C" void init() {
    // Your Qubic smart contract code here
}

extern "C" void onTick() {
    // Tick logic
}

extern "C" void onTransaction(Transaction* tx) {
    // Transaction handling
}`}
              className={`w-full p-4 bg-black/60 border border-gray-800 rounded font-mono text-sm text-[#00ff41] placeholder:text-gray-600 focus:border-[#00ff41] focus:outline-none focus:ring-1 focus:ring-[#00ff41] resize-none ${
                result && result.status === "success"
                  ? "h-[120px]"
                  : "h-[400px]"
              }`}
            />
            <Button
              onClick={handleAudit}
              disabled={loading || !code.trim()}
              className="w-full mt-4 h-12 bg-[#00ff41] text-black hover:bg-[#00cc33] font-bold font-mono uppercase disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ANALYZING...
                </>
              ) : (
                <>
                  <Shield className="h-4 w-4 mr-2" />
                  RUN SMARTGUARD ANALYSIS
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Loading Progress - Show when analyzing */}
        {loading && (
          <Card className="border-gray-800 bg-black/40 mb-6">
            <CardHeader>
              <CardTitle className="text-sm font-mono uppercase text-gray-400 flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                ANALYSIS IN PROGRESS
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {STEPS.map((step, idx) => (
                  <div
                    key={step.id}
                    className={`flex items-center gap-3 text-xs font-mono transition-all ${
                      idx < activeStep
                        ? "text-[#00ff41]"
                        : idx === activeStep
                        ? "text-yellow-500 animate-pulse"
                        : "text-gray-600"
                    }`}
                  >
                    {idx < activeStep ? (
                      <CheckCircle2 className="h-4 w-4" />
                    ) : idx === activeStep ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <div className="h-4 w-4 rounded-full border border-gray-600" />
                    )}
                    <span>{step.label}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Error Display */}
        {result && result.status === "error" && (
          <Card className="border-gray-800 bg-black/40">
            <CardContent className="pt-6">
              <div className="p-4 bg-red-900/20 border border-red-500/50 rounded text-red-500 font-mono text-sm">
                <AlertTriangle className="h-5 w-5 mb-2" />
                <p className="font-bold">ERROR</p>
                <p>{result.error || result.message || "Unknown error"}</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results - Full Width Below Code Editor */}
        {result && result.status === "success" && (
          <Card className="border-gray-800 bg-black/40">
            <CardHeader>
              <CardTitle className="text-sm font-mono uppercase text-gray-400 flex items-center gap-2">
                <FileText className="h-4 w-4" />
                AUDIT RESULTS
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col min-h-[600px]">
                {/* Tab Navigation */}
                <div className="flex flex-wrap gap-2 border-b border-gray-800 pb-2 mb-4 flex-shrink-0">
                  {result.commented && (
                    <button
                      onClick={() => setSelectedTab("commented")}
                      className={`px-3 py-1.5 text-xs font-mono rounded transition-colors ${
                        selectedTab === "commented"
                          ? "bg-[#00ff41] text-black font-bold"
                          : "bg-black/60 text-gray-400 hover:text-[#00ff41] hover:bg-black/80"
                      }`}
                    >
                      Commented Code
                    </button>
                  )}
                  {result.semantic_report && (
                    <button
                      onClick={() => setSelectedTab("semantic")}
                      className={`px-3 py-1.5 text-xs font-mono rounded transition-colors ${
                        selectedTab === "semantic"
                          ? "bg-[#00ff41] text-black font-bold"
                          : "bg-black/60 text-gray-400 hover:text-[#00ff41] hover:bg-black/80"
                      }`}
                    >
                      Semantic
                    </button>
                  )}
                  {result.audit_report && (
                    <button
                      onClick={() => setSelectedTab("audit")}
                      className={`px-3 py-1.5 text-xs font-mono rounded transition-colors ${
                        selectedTab === "audit"
                          ? "bg-[#00ff41] text-black font-bold"
                          : "bg-black/60 text-gray-400 hover:text-[#00ff41] hover:bg-black/80"
                      }`}
                    >
                      Security Audit
                    </button>
                  )}
                  {result.functional_spec && (
                    <button
                      onClick={() => setSelectedTab("spec")}
                      className={`px-3 py-1.5 text-xs font-mono rounded transition-colors ${
                        selectedTab === "spec"
                          ? "bg-[#00ff41] text-black font-bold"
                          : "bg-black/60 text-gray-400 hover:text-[#00ff41] hover:bg-black/80"
                      }`}
                    >
                      Functional Spec
                    </button>
                  )}
                  {result.flow_diagram && (
                    <button
                      onClick={() => setSelectedTab("diagram")}
                      className={`px-3 py-1.5 text-xs font-mono rounded transition-colors ${
                        selectedTab === "diagram"
                          ? "bg-[#00ff41] text-black font-bold"
                          : "bg-black/60 text-gray-400 hover:text-[#00ff41] hover:bg-black/80"
                      }`}
                    >
                      Flow Diagram
                    </button>
                  )}
                  {result.test_plan && (
                    <button
                      onClick={() => setSelectedTab("test")}
                      className={`px-3 py-1.5 text-xs font-mono rounded transition-colors ${
                        selectedTab === "test"
                          ? "bg-[#00ff41] text-black font-bold"
                          : "bg-black/60 text-gray-400 hover:text-[#00ff41] hover:bg-black/80"
                      }`}
                    >
                      Test Plan
                    </button>
                  )}
                  {result.detailed_doc && (
                    <button
                      onClick={() => setSelectedTab("docs")}
                      className={`px-3 py-1.5 text-xs font-mono rounded transition-colors ${
                        selectedTab === "docs"
                          ? "bg-[#00ff41] text-black font-bold"
                          : "bg-black/60 text-gray-400 hover:text-[#00ff41] hover:bg-black/80"
                      }`}
                    >
                      Documentation
                    </button>
                  )}
                </div>

                {/* Tab Content - Scrollable - Full Width */}
                <ScrollArea className="flex-1 max-h-[calc(100vh-400px)]">
                  <div className="pr-4">
                    {selectedTab === "commented" && (
                      <div className="bg-black/60 p-4 rounded border border-gray-800">
                        <pre className="text-[#00ff41] text-sm font-mono overflow-x-auto whitespace-pre-wrap">
                          <code>{getResultField("commented")}</code>
                        </pre>
                      </div>
                    )}

                    {selectedTab === "semantic" && (
                      <div className="bg-black/60 p-6 rounded border border-gray-800">
                        <MarkdownRenderer
                          content={getResultField("semantic_report")}
                        />
                      </div>
                    )}

                    {selectedTab === "audit" && (
                      <div className="bg-black/60 p-6 rounded border border-gray-800">
                        <MarkdownRenderer
                          content={getResultField("audit_report")}
                        />
                      </div>
                    )}

                    {selectedTab === "spec" && (
                      <div className="bg-black/60 p-6 rounded border border-gray-800">
                        <MarkdownRenderer
                          content={getResultField("functional_spec")}
                        />
                      </div>
                    )}

                    {selectedTab === "diagram" && (
                      <div className="bg-black/60 p-4 rounded border border-gray-800">
                        <MermaidDiagram
                          diagram={getResultField("flow_diagram")}
                        />
                      </div>
                    )}

                    {selectedTab === "test" && (
                      <div className="bg-black/60 p-6 rounded border border-gray-800">
                        <MarkdownRenderer
                          content={getResultField("test_plan")}
                        />
                      </div>
                    )}

                    {selectedTab === "docs" && (
                      <div className="bg-black/60 p-6 rounded border border-gray-800">
                        <MarkdownRenderer
                          content={getResultField("detailed_doc")}
                        />
                      </div>
                    )}

                    {!selectedTab && (
                      <div className="text-center text-gray-500 font-mono text-sm py-8">
                        Select a tab to view results
                      </div>
                    )}
                  </div>
                </ScrollArea>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
