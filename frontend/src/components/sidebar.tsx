import { useLocation, useNavigate } from "react-router-dom"
import { Home, Activity, MessageSquare, Network, Shield, TrendingUp, Zap, BarChart3 } from "lucide-react"
import { cn } from "../lib/utils"

const navigation = [
  { name: "Live Monitor", icon: Activity, path: "/" },
  { name: "Wallet Graph", icon: Network, path: "/graph" },
  { name: "Predictions", icon: TrendingUp, path: "/predictions" },
  { name: "Market Intel", icon: BarChart3, path: "/market-intel" },
  { name: "Attack Simulator", icon: Zap, path: "/simulator" },
  { name: "Ask Aegis", icon: MessageSquare, path: "/chat" },
]

export function Sidebar() {
  const location = useLocation()
  const navigate = useNavigate()

  return (
    <div className="flex w-64 flex-col border-r border-border bg-sidebar">
      <div className="flex h-16 items-center gap-3 border-b border-sidebar-border px-6">
        <Shield className="h-8 w-8 text-primary" />
        <div>
          <h2 className="text-lg font-bold text-primary font-mono">QUBIC</h2>
          <p className="text-xs text-muted-foreground">AEGIS v2.1</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 p-4">
        {navigation.map((item) => {
          const Icon = item.icon
          const isCurrent = location.pathname === item.path
          return (
            <button
              key={item.name}
              onClick={() => navigate(item.path)}
              className={cn(
                "flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isCurrent
                  ? "bg-sidebar-accent text-sidebar-accent-foreground border border-primary/30"
                  : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
              )}
            >
              <Icon className="h-5 w-5" />
              {item.name}
            </button>
          )
        })}
      </nav>

      <div className="border-t border-sidebar-border p-4">
        <div className="rounded-md bg-sidebar-accent p-3 border border-primary/20">
          <p className="text-xs font-mono text-muted-foreground">SYSTEM STATUS</p>
          <p className="mt-1 text-sm font-semibold text-primary">ALL SYSTEMS NOMINAL</p>
        </div>
      </div>
    </div>
  )
}

