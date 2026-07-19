import React from "react";
import { UserX, RotateCcw } from "lucide-react";

interface EmptyStateProps {
  message?: string;
  subMessage?: string;
  onClearFilters?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  message = "No faculty matched your search.",
  subMessage = "Try adjusting your search terms or department filter selection.",
  onClearFilters
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center border border-outline-variant/30 bg-surface-container-low/40 rounded-2xl w-full">
      <div className="w-12 h-12 rounded-full bg-surface-container flex items-center justify-center text-on-surface-variant/60 mb-4 select-none">
        <UserX size={24} />
      </div>
      <h4 className="text-sm font-bold text-primary mb-1 uppercase tracking-wide">
        {message}
      </h4>
      <p className="text-xs text-on-surface-variant max-w-xs leading-relaxed font-medium mb-4">
        {subMessage}
      </p>
      {onClearFilters && (
        <button
          onClick={onClearFilters}
          className="flex items-center gap-2 px-4 py-2 border border-outline-variant hover:border-primary text-[10px] font-extrabold text-primary uppercase tracking-wider rounded-lg bg-surface-container-low hover:bg-surface-variant transition-colors cursor-pointer active:scale-[0.98]"
        >
          <RotateCcw size={12} />
          <span>Clear Filters</span>
        </button>
      )}
    </div>
  );
};
