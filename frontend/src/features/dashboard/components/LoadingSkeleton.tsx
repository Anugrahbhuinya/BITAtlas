import React from "react";

export const LoadingSkeleton: React.FC = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-pulse">
      {Array.from({ length: 6 }).map((_, i) => (
        <div
          key={i}
          className="border border-outline-variant/40 bg-surface-container-low rounded-2xl p-5 space-y-4"
        >
          {/* Header block with avatar skeleton */}
          <div className="flex gap-4 items-start">
            <div className="w-12 h-12 rounded-full bg-surface-container shrink-0" />
            <div className="space-y-2 flex-1">
              <div className="h-4 bg-surface-container rounded w-3/4" />
              <div className="h-3 bg-surface-container rounded w-1/2" />
              <div className="h-3 bg-surface-container rounded w-2/5" />
            </div>
          </div>
          
          {/* Details lines skeleton */}
          <div className="space-y-2 pt-2 border-t border-outline-variant/20">
            <div className="h-3 bg-surface-container rounded w-5/6" />
            <div className="h-3 bg-surface-container rounded w-2/3" />
          </div>
          
          {/* Tags/Chips skeleton */}
          <div className="flex gap-1.5 flex-wrap pt-2">
            <div className="h-5 bg-surface-container rounded-full w-16" />
            <div className="h-5 bg-surface-container rounded-full w-20" />
            <div className="h-5 bg-surface-container rounded-full w-14" />
          </div>
        </div>
      ))}
    </div>
  );
};
