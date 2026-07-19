import React from "react";
import { AlertCircle, RefreshCw } from "lucide-react";

interface ErrorStateProps {
  message?: string;
  onRetry: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  message = "Unable to load faculty directory.",
  onRetry
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center border border-rose-500/10 bg-rose-500/5 rounded-2xl">
      <div className="w-12 h-12 rounded-full bg-rose-500/10 flex items-center justify-center text-rose-400 mb-4">
        <AlertCircle size={24} />
      </div>
      <h4 className="text-sm font-bold text-rose-400 mb-2 uppercase tracking-wide">
        {message}
      </h4>
      <button
        onClick={onRetry}
        className="flex items-center gap-2 px-4 py-2 border border-rose-500/20 hover:border-rose-400 text-[10px] font-extrabold text-rose-400 uppercase tracking-wider rounded-lg bg-rose-500/5 hover:bg-rose-500/10 transition-colors cursor-pointer active:scale-[0.98]"
      >
        <RefreshCw size={12} />
        <span>Retry</span>
      </button>
    </div>
  );
};
