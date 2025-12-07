import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import ForceGraph2D from "react-force-graph-2d";
import { apiUrl } from "../lib/api";

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
          `${apiUrl("api/wallet-graph")}?max_nodes=${maxNodes}`
        );
        const data: ApiGraphResponse = await response.json();

        if (data.nodes && data.edges && data.nodes.length > 0) {
          // Use new format with edges instead of links
          setGraphData({
            nodes: data.nodes.map((node: ApiNode, idx: number) => {
              const volume =
                node.value || (node.risk_score ? node.risk_score * 10000 : 1);
              return {
                id: node.id || `node-${idx}`,
                label: node.label || node.id?.substring(0, 10) || `Node ${idx}`,
                group:
                  node.role ||
                  node.group ||
                  (volume > 500000 ? "high_risk" : "normal"),
                value: volume,
              };
            }),
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
            nodes: data.nodes.map((node: ApiNode, idx: number) => {
              const volume =
                node.value || (node.risk_score ? node.risk_score * 10000 : 1);
              return {
                id: node.id || `node-${idx}`,
                label: node.label || node.id || `Node ${idx}`,
                group: node.group || (volume > 500000 ? "high_risk" : "normal"),
                value: volume,
              };
            }),
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
              // High Risk = Rouge vif néon
              if (node.group === "high_risk") return "#ff0000";
              // Safe = Vert foncé discret
              return "#166534";
            }}
            linkColor={() => "rgba(128, 128, 128, 0.2)"}
            linkWidth={(link: GraphLink) => 1}
            nodeCanvasObject={() => {
              // Ne pas afficher les labels par défaut (cachés)
            }}
            nodeVal={(node: GraphNode) => {
              // Whale (gros volume) = 3x plus gros
              const baseSize = 6;
              const isWhale = (node.value || 0) > 500000;
              return isWhale ? baseSize * 3 : baseSize;
            }}
            cooldownTicks={100}
            backgroundColor="#000000"
          />
        </div>
        <div className="mt-4 flex gap-4 text-xs text-muted-foreground font-mono">
          <div className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: "#166534" }}
            ></div>
            <span>Safe Wallet</span>
          </div>
          <div className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: "#ff0000" }}
            ></div>
            <span>High Risk Wallet</span>
          </div>
          <div className="flex items-center gap-2">
            <div
              className="w-3 h-3 border"
              style={{ borderColor: "rgba(128, 128, 128, 0.2)" }}
            ></div>
            <span>Connection</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
