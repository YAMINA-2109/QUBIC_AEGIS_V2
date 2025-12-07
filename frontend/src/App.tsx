import { Routes, Route } from "react-router-dom";
import { useState, useEffect } from "react";
import { Sidebar } from "./components/sidebar";
import { Header } from "./components/header";
import { LiveMonitor } from "./pages/LiveMonitor";
import { TokenIntel } from "./pages/TokenIntel";
import { WarRoom } from "./pages/WarRoom";
import { NeuralSearch } from "./pages/NeuralSearch";
import { Toaster } from "sonner";
import { ErrorBoundary } from "./components/ErrorBoundary";
import {
  ConnectionProvider,
  useConnection,
} from "./contexts/ConnectionContext";
import { cn } from "./lib/utils";

interface DEFCONStatus {
  defcon_level: number;
  alert_threshold: number;
  attacks_last_minute: number;
  status: string;
}

function AppContent() {
  const { isConnected } = useConnection();
  const [defconStatus, setDefconStatus] = useState<DEFCONStatus | null>(null);
  const [isUnderAttack, setIsUnderAttack] = useState(false);

  // Fetch DEFCON status for global attack effect
  useEffect(() => {
    const fetchDEFCON = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/defcon-status");
        if (response.ok) {
          const data = await response.json();
          setDefconStatus(data);
          setIsUnderAttack(data.defcon_level <= 2);
        }
      } catch (error) {
        // Silently fail if DEFCON endpoint not available
      }
    };

    fetchDEFCON();
    const interval = setInterval(fetchDEFCON, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      className={cn(
        "flex h-screen bg-[#050505] relative",
        isUnderAttack && "border-4 border-red-500 animate-pulse"
      )}
    >
      {/* Red overlay when under attack */}
      {isUnderAttack && (
        <div className="absolute inset-0 bg-red-500/5 pointer-events-none z-50" />
      )}

      <Toaster theme="dark" position="top-right" richColors />
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden relative">
        <Header
          isConnected={isConnected}
          defconStatus={defconStatus}
          isUnderAttack={isUnderAttack}
        />
        <Routes>
          <Route path="/" element={<LiveMonitor />} />
          <Route path="/market-intel" element={<TokenIntel />} />
          <Route path="/war-room" element={<WarRoom />} />
          <Route path="/neural-search" element={<NeuralSearch />} />
        </Routes>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <ConnectionProvider>
      <AppContent />
    </ConnectionProvider>
  );
}
