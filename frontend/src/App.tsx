import { Routes, Route } from "react-router-dom";
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

function AppContent() {
  const { isConnected } = useConnection();

  return (
    <div className="flex h-screen bg-[#050505]">
      <Toaster theme="dark" position="top-right" richColors />
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header isConnected={isConnected} />
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
