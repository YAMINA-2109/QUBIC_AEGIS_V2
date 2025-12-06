import { WalletGraphEnterprise } from "../components/wallet-graph-enterprise";

export function Graph() {
  return (
    <div className="flex-1 overflow-y-auto p-6 bg-background">
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight font-mono text-foreground">
          WALLET INTERACTION GRAPH
        </h1>
        <p className="text-sm text-muted-foreground mt-2">
          AI-powered wallet interaction visualization and cluster analysis
        </p>
      </div>
      <WalletGraphEnterprise maxNodes={100} />
    </div>
  );
}

