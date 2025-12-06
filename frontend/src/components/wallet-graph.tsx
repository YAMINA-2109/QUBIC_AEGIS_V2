import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import ForceGraph2D from "react-force-graph-2d";

interface Node {
  id: string;
  label: string;
  value: number;
  group: string;
  x?: number;
  y?: number;
}

interface Link {
  source: string | number;
  target: string | number;
  value: number;
}

interface WalletGraphProps {
  maxNodes?: number;
}

// Types for API responses
interface ApiNode {
  id: string;
  label?: string;
  role?: string;
  group?: string;
  value?: number;
  risk_score?: number;
}

interface ApiEdge {
  source: string;
  target: string;
  weight?: number;
}

interface ApiLink {
  source: string | number;
  target: string | number;
  value?: number;
}

interface ApiGraphResponse {
  nodes: ApiNode[];
  edges?: ApiEdge[];
  links?: ApiLink[];
  clusters?: Array<{
    cluster_id: string;
    wallets: string[];
    risk_level: string;
    description: string;
  }>;
}

// Type for react-force-graph node
interface GraphNode extends Node {
  x?: number;
  y?: number;
}

// Type for react-force-graph link
interface GraphLink extends Link {
  source: string | number;
  target: string | number;
}

// Données initiales pour ne jamais avoir un écran noir
const INITIAL_DEMO_DATA = {
  nodes: [
    {
      id: "Whale-Alpha",
      label: "Whale Alpha",
      value: 2000000,
      group: "high_risk",
    },
    {
      id: "Exchange-Hot",
      label: "Exchange Hot",
      value: 1500000,
      group: "normal",
    },
    { id: "Victim-1", label: "Victim Wallet 1", value: 50000, group: "normal" },
    { id: "Victim-2", label: "Victim Wallet 2", value: 30000, group: "normal" },
    {
      id: "Unknown-Attacker",
      label: "Unknown Attacker",
      value: 3000000,
      group: "high_risk",
    },
    {
      id: "Mixer-Relay",
      label: "Mixer Relay",
      value: 100000,
      group: "high_risk",
    },
    { id: "Normal-User-1", label: "User 1", value: 5000, group: "normal" },
    { id: "Normal-User-2", label: "User 2", value: 3000, group: "normal" },
    { id: "Normal-User-3", label: "User 3", value: 2000, group: "normal" },
  ],
  links: [
    { source: "Whale-Alpha", target: "Exchange-Hot", value: 5 },
    { source: "Unknown-Attacker", target: "Mixer-Relay", value: 8 },
    { source: "Mixer-Relay", target: "Victim-1", value: 3 },
    { source: "Mixer-Relay", target: "Victim-2", value: 2 },
    { source: "Exchange-Hot", target: "Unknown-Attacker", value: 6 },
    { source: "Normal-User-1", target: "Normal-User-2", value: 1 },
    { source: "Normal-User-2", target: "Normal-User-3", value: 1 },
  ],
};

export function WalletGraph({ maxNodes = 50 }: WalletGraphProps) {
  const [graphData, setGraphData] = useState<{
    nodes: GraphNode[];
    links: GraphLink[];
  }>(INITIAL_DEMO_DATA);

  useEffect(() => {
    const fetchGraphData = async () => {
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/api/wallet-graph?max_nodes=${maxNodes}`
        );
        const data: ApiGraphResponse = await response.json();

        if (data.nodes && data.edges && data.nodes.length > 0) {
          // Use new format with edges instead of links
          setGraphData({
            nodes: data.nodes.map((node: ApiNode, idx: number) => ({
              id: node.id || `node-${idx}`,
              label: node.label || node.id?.substring(0, 10) || `Node ${idx}`,
              group: node.role || node.group || "normal",
              value: node.value || 1,
            })),
            links: data.edges.map((edge: ApiEdge) => ({
              source: edge.source,
              target: edge.target,
              value: edge.weight || 1,
            })),
          });

          // Log clusters if available
          if (data.clusters && data.clusters.length > 0) {
            console.log(
              `Detected ${data.clusters.length} clusters:`,
              data.clusters
            );
          }
        } else if (data.nodes && data.links && data.nodes.length > 0) {
          // Fallback to old format
          setGraphData({
            nodes: data.nodes.map((node: ApiNode, idx: number) => ({
              id: node.id || `node-${idx}`,
              label: node.label || node.id || `Node ${idx}`,
              group: node.group || "normal",
              value: node.value || 1,
            })),
            links: data.links.map((link: ApiLink) => ({
              source:
                typeof link.source === "number"
                  ? `node-${link.source}`
                  : link.source,
              target:
                typeof link.target === "number"
                  ? `node-${link.target}`
                  : link.target,
              value: link.value || 1,
            })),
          });
        }
      } catch (error) {
        console.error("Error fetching graph data:", error);
        // Keep demo data if fetch fails
      }
    };

    fetchGraphData();

    // Refresh every 30 seconds
    const interval = setInterval(fetchGraphData, 30000);
    return () => clearInterval(interval);
  }, [maxNodes]);

  return (
    <Card className="border-primary/30">
      <CardHeader>
        <CardTitle className="text-sm font-mono uppercase text-muted-foreground">
          Wallet Interaction Graph
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[500px] rounded-md border border-border bg-black/40 relative">
          <div className="absolute top-4 left-4 z-10 bg-black/80 p-2 border border-primary text-primary font-mono text-xs">
            LIVE INTERACTION MAP
          </div>
          <ForceGraph2D
            graphData={graphData}
            nodeLabel={(node: GraphNode) =>
              `${node.label || node.id}\nVolume: ${(
                node.value || 0
              ).toLocaleString()}`
            }
            nodeColor={(node: GraphNode) => {
              if (node.group === "high_risk") return "#ff3232"; // Red for high risk
              return "#00ff41"; // Green for normal
            }}
            linkColor={() => "rgba(0, 255, 65, 0.3)"}
            linkWidth={(link: GraphLink) => Math.sqrt(link.value || 1) * 2}
            nodeCanvasObject={(
              node: GraphNode,
              ctx: CanvasRenderingContext2D,
              globalScale: number
            ) => {
              const label = node.label || node.id;
              const fontSize = 12 / globalScale;
              ctx.font = `${fontSize}px monospace`;
              ctx.textAlign = "center";
              ctx.textBaseline = "middle";
              ctx.fillStyle =
                node.group === "high_risk" ? "#ff3232" : "#00ff41";
              ctx.fillText(
                label,
                node.x || 0,
                (node.y || 0) + 10 / globalScale
              );
            }}
            nodeRelSize={6}
            cooldownTicks={100}
            backgroundColor="#000000"
          />
        </div>
        <div className="mt-4 flex gap-4 text-xs text-muted-foreground">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-neon-green"></div>
            <span>Normal Wallet</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-destructive"></div>
            <span>High Risk Wallet</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 border border-neon-green/50"></div>
            <span>Connection</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
