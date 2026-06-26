import { useState, useEffect } from "react";
import { useAdminStore } from "../hooks/adminStore";
import { Search, Bell, Moon, User, Menu, Cpu, Server, Database as DbIcon } from "lucide-react";

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
    <header className="sticky top-0 z-30 flex items-center justify-between px-6 py-4 bg-slate-950/80 backdrop-blur-md border-b border-slate-900/60 min-h-[73px]">
      {/* Search Input Bar & Mobile toggle */}
      <div className="flex items-center gap-4 flex-1">
        <button
          onClick={onMobileMenuToggle}
          className="md:hidden p-2 hover:bg-slate-900 rounded-lg text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="relative max-w-xs w-full hidden sm:block">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search console..."
            className="w-full pl-9 pr-4 py-2 text-xs bg-slate-900/40 border border-slate-800 rounded-xl text-slate-300 placeholder-slate-500 focus:outline-none focus:border-blue-500/60 focus:ring-1 focus:ring-blue-500/20 transition-all"
          />
        </div>
      </div>

      {/* Right Navbar Controls */}
      <div className="flex items-center gap-5 sm:gap-6 shrink-0">
        {/* System status dots */}
        <div className="hidden lg:flex items-center gap-4 bg-slate-900/60 border border-slate-900 px-3.5 py-1.5 rounded-xl">
          <span className="text-[10px] text-slate-400 font-semibold tracking-wider uppercase pr-1 border-r border-slate-800/80 mr-1">
            Status
          </span>
          {statusComponents.map((comp) => getStatusIcon(comp.name, comp.status))}
        </div>

        {/* Live Clock / Calendar */}
        <div className="hidden sm:flex flex-col items-end border-r border-slate-900 pr-5 select-none font-mono">
          <span className="text-sm font-semibold text-slate-100 tracking-tight">
            {formatTime(time)}
          </span>
          <span className="text-[10px] text-slate-400 uppercase tracking-wider mt-0.5">
            {formatDate(time)}
          </span>
        </div>

        {/* Action icons */}
        <div className="flex items-center gap-2">
          {/* Notifications toggle */}
          <button className="p-2.5 hover:bg-slate-900 rounded-xl text-slate-400 hover:text-slate-200 transition-colors relative cursor-pointer group" title="Notifications">
            <Bell className="w-4 h-4 group-hover:scale-105 transition-transform" />
            <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-blue-500 rounded-full glow-blue" />
          </button>

          {/* Theme Toggle (Static design mode placeholder) */}
          <button className="p-2.5 hover:bg-slate-900 rounded-xl text-slate-400 hover:text-slate-200 transition-colors cursor-pointer group" title="Theme Toggle (Dark Theme Lock)">
            <Moon className="w-4 h-4 text-blue-400 group-hover:rotate-12 transition-transform" />
          </button>
        </div>

        {/* Current user badge */}
        <div className="flex items-center gap-3 pl-2 sm:pl-4 border-l border-slate-900 select-none">
          <div className="flex flex-col items-end hidden md:flex">
            <span className="text-xs font-semibold text-slate-200">
              {username || "Administrator"}
            </span>
            <span className="text-[9px] text-slate-400 uppercase tracking-wider font-medium mt-0.5">
              Super Admin
            </span>
          </div>
          <div className="p-2 bg-slate-900 border border-slate-800 rounded-xl text-slate-300">
            <User className="w-4 h-4" />
          </div>
        </div>
      </div>
    </header>
  );
};
