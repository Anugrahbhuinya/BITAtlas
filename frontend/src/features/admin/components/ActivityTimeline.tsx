import { ShieldAlert, Key, Zap, Clock, Terminal } from "lucide-react";

export interface ActivityItem {
  _id?: string;
  id?: string;
  action: string;
  username: string;
  timestamp: string | Date;
  details?: Record<string, any>;
}

interface ActivityTimelineProps {
  activities: ActivityItem[];
  limit?: number;
}

export const ActivityTimeline = ({
  activities,
  limit = 10,
}: ActivityTimelineProps) => {
  const getIcon = (action: string) => {
    const act = action.toLowerCase();
    if (act.includes("login failed") || act.includes("failed")) {
      return (
        <div className="p-2 bg-rose-500/10 rounded-lg border border-rose-500/20 text-rose-400">
          <ShieldAlert className="w-4 h-4" />
        </div>
      );
    }
    if (act.includes("login") || act.includes("logout")) {
      return (
        <div className="p-2 bg-emerald-500/10 rounded-lg border border-emerald-500/20 text-emerald-400">
          <Key className="w-4 h-4" />
        </div>
      );
    }
    if (act.includes("system started") || act.includes("initialized")) {
      return (
        <div className="p-2 bg-blue-500/10 rounded-lg border border-blue-500/20 text-blue-400">
          <Zap className="w-4 h-4" />
        </div>
      );
    }
    return (
      <div className="p-2 bg-slate-800/80 rounded-lg border border-slate-700/50 text-slate-300">
        <Terminal className="w-4 h-4" />
      </div>
    );
  };

  const getRelativeTime = (dateInput: string | Date) => {
    try {
      const date = typeof dateInput === "string" ? new Date(dateInput) : dateInput;
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      const diffHrs = Math.floor(diffMins / 600);

      if (diffMins < 1) return "Just now";
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffHrs < 24) return `${diffHrs}h ago`;
      
      return date.toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch (e) {
      return "Recently";
    }
  };

  const items = activities.slice(0, limit);

  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center text-slate-500">
        <Clock className="w-8 h-8 opacity-40 mb-2 animate-pulse" />
        <span className="text-xs">No activity logs recorded</span>
      </div>
    );
  }

  return (
    <div className="relative border-l border-slate-800/80 pl-6 ml-3 space-y-6">
      {items.map((item, idx) => (
        <div key={item._id || item.id || idx} className="relative group">
          {/* Bullet point glow */}
          <div className="absolute -left-[31px] top-1.5 flex items-center justify-center">
            {getIcon(item.action)}
          </div>

          <div className="space-y-1">
            <div className="flex items-center justify-between gap-4">
              <h4 className="text-sm font-semibold text-slate-200 group-hover:text-white transition-colors">
                {item.action}
              </h4>
              <span className="text-xs text-slate-400 font-mono bg-slate-900 px-2 py-0.5 rounded border border-slate-800/60">
                {getRelativeTime(item.timestamp)}
              </span>
            </div>

            <p className="text-xs text-slate-400">
              Triggered by <span className="text-blue-400 font-medium">@{item.username}</span>
            </p>

            {item.details && Object.keys(item.details).length > 0 && (
              <div className="mt-2 p-2 bg-slate-950/60 rounded-lg border border-slate-900/80 text-[10px] text-slate-400 font-mono overflow-x-auto max-w-full custom-scrollbar">
                {JSON.stringify(item.details)}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};
