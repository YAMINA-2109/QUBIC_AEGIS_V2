import { useState } from "react";
import { WalletGraphEnterprise } from "../components/wallet-graph-enterprise";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { Search } from "lucide-react";

export function NeuralSearch() {
  const [searchQuery, setSearchQuery] = useState("");
  const [analyzedWallet, setAnalyzedWallet] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      return;
    }

    // TODO: Call backend API to analyze wallet
    // For now, just set it as analyzed
    setAnalyzedWallet(searchQuery.trim());
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 bg-[#050505]">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight font-mono text-[#00ff41] mb-2">
            NEURAL SEARCH
          </h1>
          <p className="text-sm text-gray-400 font-mono">
            AI-Powered Wallet Analysis & Interaction Graph
          </p>
        </div>

        {/* Search Bar */}
        <Card className="mb-6 border-gray-800 bg-black/40">
          <CardContent className="pt-6">
            <div className="flex gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <Input
                  type="text"
                  placeholder="Enter Wallet ID or Contract Hash"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="pl-12 h-14 text-lg font-mono bg-black/60 border-gray-800 text-[#00ff41] placeholder:text-gray-600 focus:border-[#00ff41] focus:ring-1 focus:ring-[#00ff41]"
                />
              </div>
              <Button
                onClick={handleSearch}
                disabled={!searchQuery.trim()}
                className="h-14 px-8 bg-[#00ff41] text-black hover:bg-[#00cc33] font-bold font-mono uppercase disabled:opacity-50 disabled:cursor-not-allowed"
              >
                ANALYZE
              </Button>
            </div>
            {analyzedWallet && (
              <div className="mt-4 text-sm font-mono text-green-500">
                Analyzing wallet: <span className="font-bold">{analyzedWallet.substring(0, 20)}...</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Graph Visualization */}
        <Card className="border-gray-800 bg-black/40">
          <CardHeader>
            <CardTitle className="text-sm font-mono uppercase text-gray-400">
              WALLET INTERACTION GRAPH
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[600px] rounded-lg overflow-hidden border border-gray-800">
              <WalletGraphEnterprise maxNodes={150} />
            </div>
          </CardContent>
        </Card>

        {/* Legend */}
        <Card className="mt-6 border-gray-800 bg-black/40">
          <CardHeader>
            <CardTitle className="text-sm font-mono uppercase text-gray-400">
              LEGEND
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono text-gray-400">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
                <span>Safe Wallet</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <span>Medium Risk</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <span>High Risk</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-purple-500"></div>
                <span>Whale Wallet</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

