import { Routes, Route, useLocation } from "react-router-dom";
import { useState, useEffect } from "react";
import { Sidebar } from "./components/sidebar";
import { Header } from "./components/header";
import { LiveMonitor } from "./pages/LiveMonitor";
import { TokenIntel } from "./pages/TokenIntel";
import { WarRoom } from "./pages/WarRoom";
import { NeuralSearch } from "./pages/NeuralSearch";
import { SmartGuard } from "./pages/SmartGuard";
import { Toaster } from "sonner";
import {
  ConnectionProvider,
  useConnection,
} from "./contexts/ConnectionContext";
import { cn } from "./lib/utils";
import { apiUrl } from "./lib/api";

interface DEFCONStatus {
  defcon_level: number;
  alert_threshold: number;
  attacks_last_minute: number;
  status: string;
}

function AppContent() {
  const { isConnected } = useConnection();
  const location = useLocation();
  const [defconStatus, setDefconStatus] = useState<DEFCONStatus | null>(null);
  const [isUnderAttack, setIsUnderAttack] = useState(false);

  // Only show pulsing border on Live Monitor page
  const isLiveMonitorPage = location.pathname === "/";
  const shouldShowPulsing = isUnderAttack && isLiveMonitorPage;

  // Fetch DEFCON status for global attack effect
  useEffect(() => {
    const fetchDEFCON = async () => {
      try {
        const response = await fetch(apiUrl("api/defcon-status"));
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
        shouldShowPulsing && "border-4 border-red-500 gentle-pulse"
      )}
    >
      {/* Red overlay when under attack - only on Live Monitor */}
      {shouldShowPulsing && (
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
          <Route path="/smart-guard" element={<SmartGuard />} />
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
