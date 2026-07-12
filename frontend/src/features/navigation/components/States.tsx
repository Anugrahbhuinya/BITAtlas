// src/features/navigation/components/States.tsx

import React from "react";
import { Loader2, AlertCircle, MapPin } from "lucide-react";

export const LoadingState: React.FC<{ message?: string }> = ({ message = "Loading campus data..." }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center min-h-[200px]">
      <Loader2 className="w-10 h-10 animate-spin text-primary mb-3" />
      <p className="text-sm text-on-surface/75 font-medium">{message}</p>
    </div>
  );
};

export const ErrorState: React.FC<{ message: string; onRetry?: () => void }> = ({ message, onRetry }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center min-h-[200px] border border-error/20 bg-error/5 rounded-xl backdrop-blur-md">
      <AlertCircle className="w-10 h-10 text-error mb-3" />
      <p className="text-sm font-semibold text-error mb-1">Failed to Load</p>
      <p className="text-xs text-on-surface/70 mb-4 max-w-xs">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-1.5 bg-error text-background rounded-lg text-xs font-semibold hover:bg-error/95 transition duration-200"
        >
          Try Again
        </button>
      )}
    </div>
  );
};

export const EmptyState: React.FC<{ title?: string; message?: string }> = ({
  title = "No Locations Found",
  message = "Try adjusting your search filters or check your spelling."
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center min-h-[200px] border border-outline-variant/50 bg-surface-variant/20 rounded-xl backdrop-blur-md">
      <MapPin className="w-10 h-10 text-on-surface/40 mb-3" />
      <p className="text-sm font-bold text-on-surface/80 mb-1">{title}</p>
      <p className="text-xs text-on-surface/60 max-w-xs">{message}</p>
    </div>
  );
};
