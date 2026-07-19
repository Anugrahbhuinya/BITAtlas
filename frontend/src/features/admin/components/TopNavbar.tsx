import { useState, useEffect } from "react";
import { useAdminStore } from "../hooks/adminStore";
import { Search, User, Menu, Cpu, Server, Database as DbIcon } from "lucide-react";

interface StatusItem {
  name: string;
  status: string;
}

interface TopNavbarProps {
  statusComponents: StatusItem[];
  onMobileMenuToggle: () => void;
}

export const TopNavbar = ({ statusComponents, onMobileMenuToggle }: TopNavbarProps) => {
  const { username } = useAdminStore();
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString(undefined, {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString(undefined, {
      weekday: "short",
      month: "short",
      day: "numeric",
    });
  };

  // Map status names to specific icons
  const getStatusIcon = (name: string, status: string) => {
    const isOk = status.toLowerCase() === "connected";
    const title = `${name}: ${status}`;
    
    if (name.toLowerCase().includes("mongodb")) {
      return (
        <div key={name} className="flex items-center gap-1.5 cursor-help" title={title}>
          <DbIcon className={`w-3.5 h-3.5 ${isOk ? "text-emerald-400" : "text-rose-400"}`} />
          <span className={`w-1.5 h-1.5 rounded-full ${isOk ? "bg-emerald-400 animate-pulse" : "bg-rose-500"}`} />
        </div>
      );
    }
    if (name.toLowerCase().includes("gemini")) {
      return (
        <div key={name} className="flex items-center gap-1.5 cursor-help" title={title}>
          <Cpu className={`w-3.5 h-3.5 ${isOk ? "text-blue-400" : "text-rose-400"}`} />
          <span className={`w-1.5 h-1.5 rounded-full ${isOk ? "bg-blue-400 animate-pulse" : "bg-rose-500"}`} />
        </div>
      );
    }
    if (name.toLowerCase().includes("chromadb")) {
      return (
        <div key={name} className="flex items-center gap-1.5 cursor-help" title={title}>
          <Server className={`w-3.5 h-3.5 ${isOk ? "text-indigo-400" : "text-rose-400"}`} />
          <span className={`w-1.5 h-1.5 rounded-full ${isOk ? "bg-indigo-400 animate-pulse" : "bg-rose-500"}`} />
        </div>
      );
    }
    return null;
  };

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between px-6 py-4 bg-background/80 backdrop-blur-md border-b border-outline-variant/60 min-h-[73px]">
      {/* Search Input Bar & Mobile toggle */}
      <div className="flex items-center gap-4 flex-1">
        <button
          onClick={onMobileMenuToggle}
          className="md:hidden p-2 hover:bg-surface-container/60 rounded-lg text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="relative max-w-xs w-full hidden sm:block">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-on-surface-variant/40" />
          <input
            type="text"
            placeholder="Search console..."
            className="w-full pl-9 pr-4 py-2 text-xs bg-surface-container/40 border border-outline-variant rounded-xl text-on-surface placeholder-on-surface-variant/40 focus:outline-none focus:border-primary/60 focus:ring-1 focus:ring-primary/20 transition-all"
          />
        </div>
      </div>

      {/* Right Navbar Controls */}
      <div className="flex items-center gap-5 sm:gap-6 shrink-0">
        {/* System status dots */}
        <div className="hidden lg:flex items-center gap-4 bg-surface-container/60 border border-outline-variant px-3.5 py-1.5 rounded-xl">
          <span className="text-[10px] text-on-surface-variant font-semibold tracking-wider uppercase pr-1 border-r border-outline-variant/80 mr-1">
            Status
          </span>
          {statusComponents.map((comp) => getStatusIcon(comp.name, comp.status))}
        </div>

        {/* Live Clock / Calendar */}
        <div className="hidden sm:flex flex-col items-end border-r border-outline-variant pr-5 select-none font-mono-code">
          <span className="text-sm font-semibold text-on-surface tracking-tight">
            {formatTime(time)}
          </span>
          <span className="text-[10px] text-on-surface-variant uppercase tracking-wider mt-0.5">
            {formatDate(time)}
          </span>
        </div>



        {/* Current user badge */}
        <div className="flex items-center gap-3 pl-2 sm:pl-4 border-l border-outline-variant select-none">
          <div className="flex flex-col items-end hidden md:flex">
            <span className="text-xs font-semibold text-on-surface">
              {username || "Administrator"}
            </span>
            <span className="text-[9px] text-on-surface-variant uppercase tracking-wider font-medium mt-0.5">
              Super Admin
            </span>
          </div>
          <div className="p-2 bg-surface-container border border-outline-variant rounded-xl text-on-surface-variant">
            <User className="w-4 h-4" />
          </div>
        </div>
      </div>
    </header>
  );
};
