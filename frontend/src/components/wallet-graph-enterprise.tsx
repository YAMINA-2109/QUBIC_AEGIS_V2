import { useEffect, useState, useRef, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import ForceGraph2D from "react-force-graph-2d";
import { Button } from "./ui/button";
import { ZoomIn, ZoomOut, RotateCcw, Filter } from "lucide-react";
import { apiUrl } from "../lib/api";

interface Node {
  id: string;
  label: string;
  value: number;
  group: string;
  risk_score?: number;
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

interface GraphNode extends Node {
  x?: number;
  y?: number;
}

interface GraphLink extends Link {
  source: string | number;
  target: string | number;
}

// Enterprise-grade initial demo data
const INITIAL_DEMO_DATA = {
  nodes: [
    {
      id: "Whale-Alpha",
      label: "Whale Alpha",
      value: 2000000,
      group: "high_risk",
      risk_score: 85,
    },
    {
      id: "Exchange-Hot",
      label: "Exchange Hot",
      value: 1500000,
      group: "normal",
      risk_score: 15,
    },
    {
      id: "Victim-1",
      label: "Victim 1",
      value: 50000,
      group: "normal",
      risk_score: 20,
    },
    {
      id: "Victim-2",
      label: "Victim 2",
      value: 30000,
      group: "normal",
      risk_score: 25,
    },
    {
      id: "Unknown-Attacker",
      label: "Attacker",
      value: 3000000,
      group: "high_risk",
      risk_score: 95,
    },
    {
      id: "Mixer-Relay",
      label: "Mixer",
      value: 100000,
      group: "high_risk",
      risk_score: 80,
    },
  ],
  links: [
    { source: "Whale-Alpha", target: "Exchange-Hot", value: 5 },
    { source: "Unknown-Attacker", target: "Mixer-Relay", value: 8 },
    { source: "Mixer-Relay", target: "Victim-1", value: 3 },
    { source: "Mixer-Relay", target: "Victim-2", value: 2 },
    { source: "Exchange-Hot", target: "Unknown-Attacker", value: 6 },
  ],
};

export function WalletGraphEnterprise({ maxNodes = 50 }: WalletGraphProps) {
  const fgRef = useRef<any>();
  const [graphData, setGraphData] = useState<{
    nodes: GraphNode[];
    links: GraphLink[];
  }>(INITIAL_DEMO_DATA);

  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [zoom, setZoom] = useState(1);
  const [filterRisk, setFilterRisk] = useState<string>("all"); // all, high, normal

  useEffect(() => {
    const fetchGraphData = async () => {
      try {
        const response = await fetch(
          `${apiUrl("api/wallet-graph")}?max_nodes=${maxNodes}`
        );
        const data: ApiGraphResponse = await response.json();

        if (data.nodes && data.nodes.length > 0) {
          let processedNodes: GraphNode[] = [];
          let processedLinks: GraphLink[] = [];

          // Process nodes
          if (data.edges) {
            processedNodes = data.nodes.map((node: ApiNode, idx: number) => ({
              id: node.id || `node-${idx}`,
              label:
                node.label || node.id?.substring(0, 12) || `Wallet ${idx + 1}`,
              group: node.role || node.group || "normal",
              value: node.value || node.risk_score || 1,
              risk_score: node.risk_score || 0,
            }));

            processedLinks = data.edges.map((edge: ApiEdge) => ({
              source: edge.source,
              target: edge.target,
              value: edge.weight || 1,
            }));
          } else if (data.links) {
            processedNodes = data.nodes.map((node: ApiNode, idx: number) => ({
              id: node.id || `node-${idx}`,
              label: node.label || node.id || `Node ${idx}`,
              group: node.group || "normal",
              value: node.value || 1,
              risk_score: node.risk_score || 0,
            }));

            processedLinks = data.links.map((link: ApiLink) => ({
              source:
                typeof link.source === "number"
                  ? `node-${link.source}`
                  : link.source,
              target:
                typeof link.target === "number"
                  ? `node-${link.target}`
                  : link.target,
              value: link.value || 1,
            }));
          }

          // Apply risk filter
          if (filterRisk !== "all") {
            const filteredNodes = processedNodes.filter((node) =>
              filterRisk === "high"
                ? node.risk_score && node.risk_score > 70
                : node.risk_score && node.risk_score <= 70
            );
            const nodeIds = new Set(filteredNodes.map((n) => n.id));
            processedLinks = processedLinks.filter(
              (link) =>
                nodeIds.has(String(link.source)) &&
                nodeIds.has(String(link.target))
            );
            processedNodes = filteredNodes;
          }

          setGraphData({
            nodes: processedNodes,
            links: processedLinks,
          });

          if (data.clusters && data.clusters.length > 0) {
            console.log(
              `Detected ${data.clusters.length} clusters:`,
              data.clusters
            );
          }
        }
      } catch (error) {
        console.error("Error fetching graph data:", error);
      }
    };

    fetchGraphData();
    const interval = setInterval(fetchGraphData, 30000);
    return () => clearInterval(interval);
  }, [maxNodes, filterRisk]);

  const handleZoomIn = useCallback(() => {
    if (fgRef.current) {
      fgRef.current.zoom(1.5, 1000);
      setZoom((z) => z * 1.5);
    }
  }, []);

  const handleZoomOut = useCallback(() => {
    if (fgRef.current) {
      fgRef.current.zoom(0.67, 1000);
      setZoom((z) => z * 0.67);
    }
  }, []);

  const handleReset = useCallback(() => {
    if (fgRef.current) {
      fgRef.current.zoomToFit(400);
      setZoom(1);
      setSelectedNode(null);
    }
  }, []);

  const getNodeColor = (node: GraphNode): string => {
    const riskScore = node.risk_score || 0;
    if (riskScore > 80) return "#ff4444"; // Critical red
    if (riskScore > 60) return "#ff8844"; // High orange
    if (riskScore > 40) return "#ffaa44"; // Medium yellow
    return "#00ff88"; // Safe green
  };

  const getNodeSize = (node: GraphNode): number => {
    const baseSize = 8;
    const riskMultiplier = (node.risk_score || 0) / 100;
    const volumeMultiplier = Math.log10((node.value || 1) + 1) / 3;
    return baseSize + riskMultiplier * 10 + volumeMultiplier * 5;
  };

  return (
    <Card className="border-primary/30">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-mono uppercase text-primary">
            Wallet Interaction Graph
          </CardTitle>
          <div className="flex items-center gap-2">
            <select
              value={filterRisk}
              onChange={(e) => setFilterRisk(e.target.value)}
              className="text-xs bg-background border border-border rounded px-2 py-1 font-mono text-foreground"
            >
              <option value="all">All Wallets</option>
              <option value="high">High Risk Only</option>
              <option value="normal">Normal Only</option>
            </select>
            <Button
              variant="outline"
              size="sm"
              onClick={handleZoomIn}
              className="h-7 w-7 p-0"
            >
              <ZoomIn className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleZoomOut}
              className="h-7 w-7 p-0"
            >
              <ZoomOut className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleReset}
              className="h-7 w-7 p-0"
            >
              <RotateCcw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-[600px] rounded-lg border-2 border-primary/20 bg-gradient-to-br from-black via-gray-950 to-black relative overflow-hidden">
          {/* Overlay stats */}
          <div className="absolute top-4 left-4 z-10 bg-black/90 backdrop-blur-sm p-3 border border-primary/40 rounded-md shadow-lg">
            <div className="text-xs font-mono text-primary mb-2">
              NETWORK STATS
            </div>
            <div className="space-y-1 text-xs text-foreground">
              <div>
                Nodes:{" "}
                <span className="text-primary font-bold">
                  {graphData.nodes.length}
                </span>
              </div>
              <div>
                Connections:{" "}
                <span className="text-primary font-bold">
                  {graphData.links.length}
                </span>
              </div>
              <div>
                High Risk:{" "}
                <span className="text-destructive font-bold">
                  {
                    graphData.nodes.filter((n) => (n.risk_score || 0) > 70)
                      .length
                  }
                </span>
              </div>
            </div>
          </div>

          {/* Selected node info */}
          {selectedNode && (
            <div className="absolute top-4 right-4 z-10 bg-black/90 backdrop-blur-sm p-3 border border-primary/40 rounded-md shadow-lg max-w-xs">
              <div className="text-xs font-mono text-primary mb-2">
                WALLET DETAILS
              </div>
              <div className="space-y-1 text-xs text-foreground">
                <div className="font-bold text-primary break-all">
                  {selectedNode.label}
                </div>
                <div>
                  ID:{" "}
                  <span className="text-muted-foreground font-mono text-[10px]">
                    {selectedNode.id}
                  </span>
                </div>
                <div>
                  Risk:{" "}
                  <span
                    className={`font-bold ${
                      (selectedNode.risk_score || 0) > 70
                        ? "text-destructive"
                        : "text-primary"
                    }`}
                  >
                    {(selectedNode.risk_score || 0).toFixed(1)}%
                  </span>
                </div>
                <div>
                  Volume:{" "}
                  <span className="text-primary font-mono">
                    {(selectedNode.value || 0).toLocaleString()}
                  </span>
                </div>
                <div>
                  Type:{" "}
                  <span className="uppercase text-muted-foreground">
                    {selectedNode.group}
                  </span>
                </div>
              </div>
            </div>
          )}

          <ForceGraph2D
            ref={fgRef}
            graphData={graphData}
            nodeLabel={(node: GraphNode) => {
              const risk = node.risk_score || 0;
              return `${node.label || node.id}\nRisk: ${risk.toFixed(
                1
              )}%\nVolume: ${(node.value || 0).toLocaleString()}`;
            }}
            nodeColor={getNodeColor}
            nodeVal={getNodeSize}
            linkColor={() => "rgba(0, 255, 136, 0.4)"}
            linkWidth={(link: GraphLink) => Math.sqrt(link.value || 1) * 1.5}
            linkDirectionalArrowLength={4}
            linkDirectionalArrowRelPos={1}
            linkCurvature={0.1}
            onNodeClick={(node: GraphNode) => {
              setSelectedNode(node);
            }}
            onBackgroundClick={() => setSelectedNode(null)}
            nodeCanvasObject={(
              node: GraphNode,
              ctx: CanvasRenderingContext2D,
              globalScale: number
            ) => {
              const label = (node.label || node.id).substring(0, 12);
              const fontSize = 11 / Math.max(globalScale, 0.5);
              ctx.font = `bold ${fontSize}px 'Courier New', monospace`;
              ctx.textAlign = "center";
              ctx.textBaseline = "middle";

              // Text shadow for better readability
              ctx.shadowColor = "rgba(0, 0, 0, 0.8)";
              ctx.shadowBlur = 4;
              ctx.shadowOffsetX = 1;
              ctx.shadowOffsetY = 1;

              ctx.fillStyle = getNodeColor(node);
              ctx.fillText(
                label,
                node.x || 0,
                (node.y || 0) + getNodeSize(node) * 0.8
              );

              // Reset shadow
              ctx.shadowBlur = 0;
            }}
            nodeRelSize={10}
            cooldownTicks={150}
            backgroundColor="transparent"
            linkOpacity={0.6}
            d3VelocityDecay={0.3}
            d3AlphaDecay={0.02}
          />
        </div>

        {/* Legend */}
        <div className="mt-4 flex flex-wrap gap-6 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-[#00ff88] border border-primary/30"></div>
            <span className="text-muted-foreground">Safe (0-40%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-[#ffaa44] border border-primary/30"></div>
            <span className="text-muted-foreground">Medium (40-60%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-[#ff8844] border border-primary/30"></div>
            <span className="text-muted-foreground">High (60-80%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-[#ff4444] border border-primary/30"></div>
            <span className="text-muted-foreground">Critical (80-100%)</span>
          </div>
          <div className="flex items-center gap-2 ml-auto">
            <div className="w-8 h-0.5 bg-primary/40"></div>
            <span className="text-muted-foreground">Connection</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
