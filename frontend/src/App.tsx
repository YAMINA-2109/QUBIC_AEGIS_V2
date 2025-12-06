import { Routes, Route } from "react-router-dom";
import { Sidebar } from "./components/sidebar";
import { Header } from "./components/header";
import { Dashboard } from "./pages/Dashboard";
import { Chat } from "./pages/Chat";
import { Graph } from "./pages/Graph";
import { Predictions } from "./pages/Predictions";
import { Simulator } from "./pages/Simulator";
import { TokenIntel } from "./pages/TokenIntel";
import { Toaster } from "sonner";
import {
  ConnectionProvider,
  useConnection,
} from "./contexts/ConnectionContext";

function AppContent() {
  const { isConnected } = useConnection();

  return (
    <div className="flex h-screen bg-background">
      <Toaster theme="dark" position="top-right" richColors />
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header isConnected={isConnected} />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/graph" element={<Graph />} />
          <Route path="/predictions" element={<Predictions />} />
          <Route path="/market-intel" element={<TokenIntel />} />
          <Route path="/simulator" element={<Simulator />} />
          <Route path="/chat" element={<Chat />} />
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
