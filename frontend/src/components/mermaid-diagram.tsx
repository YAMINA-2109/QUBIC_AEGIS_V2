/**
 * Mermaid Diagram Component
 * Renders Mermaid diagrams visually using the Mermaid.js library
 */
import { useEffect, useRef, useState } from "react";
import { cn } from "../lib/utils";
import { Loader2, AlertCircle } from "lucide-react";

interface MermaidDiagramProps {
  diagram: string;
  className?: string;
}

export function MermaidDiagram({ diagram, className }: MermaidDiagramProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [diagramId] = useState(
    () => `mermaid-${Math.random().toString(36).substr(2, 9)}`
  );

  useEffect(() => {
    if (!diagram || !containerRef.current) return;

    setIsLoading(true);
    setError(null);

    // Load Mermaid dynamically
    const loadMermaid = async () => {
      try {
        // Import Mermaid from CDN
        interface MermaidWindow extends Window {
          mermaid?: {
            initialize: (config: Record<string, unknown>) => void;
            render: (id: string, code: string) => Promise<{ svg: string }>;
          };
        }

        if (!(window as MermaidWindow).mermaid) {
          const script = document.createElement("script");
          script.src =
            "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js";
          script.async = true;
          await new Promise<void>((resolve, reject) => {
            script.onload = () => resolve();
            script.onerror = () => reject(new Error("Failed to load Mermaid"));
            document.head.appendChild(script);
          });
        }

        const mermaid = (window as MermaidWindow).mermaid;
        if (!mermaid) {
          throw new Error("Mermaid library failed to load");
        }

        // Initialize Mermaid with cyberpunk theme
        mermaid.initialize({
          startOnLoad: false,
          theme: "dark",
          themeVariables: {
            primaryColor: "#00ff41",
            primaryTextColor: "#ffffff",
            primaryBorderColor: "#00ff41",
            lineColor: "#666666",
            secondaryColor: "#050505",
            tertiaryColor: "#1a1a1a",
            background: "#050505",
            mainBkg: "#0a0a0a",
            textColor: "#ffffff",
            secondaryTextColor: "#00ff41",
            cScale0: "#00ff41",
            cScale1: "#00cc33",
            cScale2: "#ff0000",
          },
          flowchart: {
            curve: "basis",
            htmlLabels: true,
          },
        });

        // Extract mermaid code from markdown code blocks or use as-is
        let mermaidCode = diagram.trim();

        // Try to extract from markdown code block
        const mermaidBlockMatch = mermaidCode.match(
          /```mermaid\s*\n?([\s\S]*?)```/i
        );
        if (mermaidBlockMatch) {
          mermaidCode = mermaidBlockMatch[1].trim();
        } else {
          // Remove ```mermaid and ``` if present (without newlines)
          mermaidCode = mermaidCode.replace(/^```mermaid\s*/i, "");
          mermaidCode = mermaidCode.replace(/^```\s*/i, "");
          mermaidCode = mermaidCode.replace(/```\s*$/i, "");
          mermaidCode = mermaidCode.trim();
        }

        // Remove any remaining markdown formatting
        mermaidCode = mermaidCode.replace(/^Mermaid Diagram:\s*/i, "");
        mermaidCode = mermaidCode.replace(/^Diagram:\s*/i, "");
        mermaidCode = mermaidCode.trim();

        if (!mermaidCode) {
          throw new Error("Empty Mermaid diagram");
        }

        // Clear container
        if (containerRef.current) {
          containerRef.current.innerHTML = "";

          // Render diagram
          const svg = await mermaid.render(diagramId, mermaidCode);

          if (containerRef.current && svg.svg) {
            containerRef.current.innerHTML = svg.svg;
          }
        }

        setIsLoading(false);
      } catch (err) {
        console.error("Mermaid rendering error:", err);
        const errorMessage =
          err instanceof Error ? err.message : "Failed to render diagram";
        setError(errorMessage);
        setIsLoading(false);
      }
    };

    const currentContainer = containerRef.current;
    loadMermaid();

    // Cleanup
    return () => {
      if (currentContainer) {
        currentContainer.innerHTML = "";
      }
    };
  }, [diagram, diagramId]);

  if (!diagram) {
    return (
      <div
        className={cn(
          "p-4 text-gray-500 text-sm font-mono text-center",
          className
        )}
      >
        No diagram provided
      </div>
    );
  }

  if (error) {
    return (
      <div
        className={cn(
          "p-4 bg-red-900/20 border border-red-500/50 rounded",
          className
        )}
      >
        <div className="flex items-center gap-2 text-red-500 text-sm font-mono mb-2">
          <AlertCircle className="h-4 w-4" />
          <span className="font-bold">DIAGRAM RENDER ERROR</span>
        </div>
        <pre className="text-xs text-red-400 overflow-x-auto">{error}</pre>
        <details className="mt-4">
          <summary className="text-xs text-red-400 cursor-pointer mb-2">
            Raw Diagram Code
          </summary>
          <pre className="text-xs text-gray-500 bg-black/60 p-2 rounded overflow-x-auto">
            {diagram}
          </pre>
        </details>
      </div>
    );
  }

  return (
    <div className={cn("relative", className)}>
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/60 rounded">
          <div className="flex flex-col items-center gap-2 text-[#00ff41]">
            <Loader2 className="h-8 w-8 animate-spin" />
            <span className="text-sm font-mono">Rendering Diagram...</span>
          </div>
        </div>
      )}
      <div
        ref={containerRef}
        className={cn(
          "mermaid-diagram bg-white/5 rounded border border-gray-700 p-4 overflow-auto",
          isLoading && "opacity-0"
        )}
        style={{
          minHeight: "300px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      />
    </div>
  );
}
