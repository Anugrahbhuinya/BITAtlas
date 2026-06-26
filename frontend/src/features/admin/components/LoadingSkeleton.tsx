export const SkeletonPulse = ({ className = "" }: { className?: string }) => {
  return (
    <div className={`animate-pulse bg-slate-800/60 rounded ${className}`} />
  );
};

export const CardSkeleton = () => {
  return (
    <div className="glass-panel p-6 rounded-2xl border border-slate-800/40 space-y-4">
      <div className="flex justify-between items-center">
        <SkeletonPulse className="w-1/3 h-5" />
        <SkeletonPulse className="w-8 h-8 rounded-lg" />
      </div>
      <SkeletonPulse className="w-1/2 h-8" />
      <div className="space-y-2 pt-2">
        <SkeletonPulse className="w-full h-3" />
        <SkeletonPulse className="w-2/3 h-3" />
      </div>
    </div>
  );
};

export const TableSkeleton = ({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) => {
  return (
    <div className="w-full space-y-4">
      {/* Header skeleton */}
      <div className="flex gap-4 p-4 border-b border-slate-800/40">
        {Array.from({ length: cols }).map((_, i) => (
          <SkeletonPulse key={i} className="flex-1 h-5" />
        ))}
      </div>
      {/* Body skeleton */}
      <div className="space-y-3">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="flex gap-4 p-4 rounded-xl border border-slate-800/20 bg-slate-900/10">
            {Array.from({ length: cols }).map((_, j) => (
              <SkeletonPulse key={j} className="flex-1 h-5" />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export const ListSkeleton = ({ items = 3 }: { items?: number }) => {
  return (
    <div className="space-y-4">
      {Array.from({ length: items }).map((_, i) => (
        <div key={i} className="flex gap-4 items-center">
          <SkeletonPulse className="w-10 h-10 rounded-full" />
          <div className="flex-1 space-y-2">
            <SkeletonPulse className="w-1/4 h-4" />
            <SkeletonPulse className="w-1/2 h-3" />
          </div>
        </div>
      ))}
    </div>
  );
};
