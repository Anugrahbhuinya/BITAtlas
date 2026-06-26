import { FolderOpen } from "lucide-react";

interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: React.ReactNode;
  actionLabel?: string;
  onAction?: () => void;
}

export const EmptyState = ({
  title = "No results found",
  description = "Try adjusting your search terms or filter constraints.",
  icon = <FolderOpen className="w-12 h-12 text-slate-500 opacity-60" />,
  actionLabel,
  onAction,
}: EmptyStateProps) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center glass-panel rounded-2xl border border-slate-800/40">
      <div className="mb-4 p-3 bg-slate-900/50 rounded-2xl border border-slate-800/60">
        {icon}
      </div>
      <h3 className="text-base font-semibold text-slate-200 mb-1">{title}</h3>
      <p className="text-sm text-slate-400 max-w-sm mb-6 leading-relaxed">
        {description}
      </p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-500 rounded-xl transition-all cursor-pointer shadow-lg hover:shadow-blue-500/20"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
};
