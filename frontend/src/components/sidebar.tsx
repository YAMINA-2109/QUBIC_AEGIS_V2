import { useLocation, useNavigate } from "react-router-dom"
import { Activity, BarChart3, Zap, Search, Shield } from "lucide-react"
import { cn } from "../lib/utils"

const navigation = [
  { name: "Live Monitor", icon: Activity, path: "/" },
  { name: "Market Intel", icon: BarChart3, path: "/market-intel" },
  { name: "War Room", icon: Zap, path: "/war-room" },
  { name: "Neural Search", icon: Search, path: "/neural-search" },
]

export function Sidebar() {
  const location = useLocation()
  const navigate = useNavigate()

  return (
    <div className="flex w-64 flex-col border-r border-gray-800 bg-[#0a0a0a]">
      <div className="flex h-16 items-center gap-3 border-b border-gray-800 px-6">
        <Shield className="h-8 w-8 text-[#00ff41]" />
        <div>
          <h2 className="text-lg font-bold text-[#00ff41] font-mono">QUBIC</h2>
          <p className="text-xs text-gray-400 font-mono">AEGIS ENTERPRISE</p>
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
                "flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors font-mono",
                isCurrent
                  ? "bg-black/60 text-[#00ff41] border border-[#00ff41]/30"
                  : "text-gray-400 hover:bg-black/40 hover:text-[#00ff41]"
              )}
            >
              <Icon className="h-5 w-5" />
              {item.name}
            </button>
          )
        })}
      </nav>

      <div className="border-t border-gray-800 p-4">
        <div className="rounded-md bg-black/60 p-3 border border-gray-800">
          <p className="text-xs font-mono text-gray-400">SYSTEM STATUS</p>
          <p className="mt-1 text-sm font-semibold text-[#00ff41] font-mono">ALL SYSTEMS NOMINAL</p>
        </div>
      </div>
    </div>
  )
}

