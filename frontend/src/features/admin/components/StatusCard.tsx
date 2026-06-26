import { CheckCircle, AlertOctagon, RefreshCw } from "lucide-react";

interface StatusCardProps {
  name: string;
  status: string;
  details?: string;
}

export const StatusCard = ({ name, status, details }: StatusCardProps) => {
  const isConnected = status.toLowerCase() === "connected";
  const isWarning = status.toLowerCase() === "warning" || status.toLowerCase() === "disconnected";
  
  return (
    <div className="glass-panel p-4 rounded-xl border border-slate-800/40 hover:border-slate-800 transition-all flex items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg border ${
          isConnected 
            ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" 
            : isWarning
            ? "bg-amber-500/10 border-amber-500/20 text-amber-400"
            : "bg-rose-500/10 border-rose-500/20 text-rose-400"
        }`}>
          {isConnected ? (
            <CheckCircle className="w-4 h-4" />
          ) : isWarning ? (
            <RefreshCw className="w-4 h-4 animate-spin-slow" />
          ) : (
            <AlertOctagon className="w-4 h-4" />
          )}
        </div>

        <div>
          <h4 className="text-xs font-semibold text-slate-200">{name}</h4>
          {details && (
            <p className="text-[10px] text-slate-400 mt-0.5 truncate max-w-[200px]" title={details}>
              {details}
            </p>
          )}
        </div>
      </div>

      <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full border text-[10px] font-semibold ${
        isConnected 
          ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" 
          : isWarning
          ? "bg-amber-500/10 border-amber-500/20 text-amber-400"
          : "bg-rose-500/10 border-rose-500/20 text-rose-400"
      }`}>
        <span className={`w-1.5 h-1.5 rounded-full ${
          isConnected 
            ? "bg-emerald-400 animate-pulse" 
            : isWarning 
            ? "bg-amber-400" 
            : "bg-rose-400"
        }`} />
        <span>{status}</span>
      </div>
    </div>
  );
};
