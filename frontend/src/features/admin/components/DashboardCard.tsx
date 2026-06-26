import type { ReactNode } from "react";

interface DashboardCardProps {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  actions?: ReactNode;
  className?: string;
}

export const DashboardCard = ({
  title,
  subtitle,
  children,
  actions,
  className = "",
}: DashboardCardProps) => {
  return (
    <div className={`glass-panel rounded-2xl p-6 border border-slate-800/40 relative overflow-hidden flex flex-col ${className}`}>
      {/* Background glass gradient effect */}
      <div className="absolute top-0 right-0 -mr-16 -mt-16 w-32 h-32 bg-blue-500/5 rounded-full blur-2xl pointer-events-none" />

      {/* Header */}
      {(title || subtitle || actions) && (
        <div className="flex items-center justify-between gap-4 mb-5">
          <div>
            {title && (
              <h3 className="text-base font-semibold text-slate-100 tracking-tight">
                {title}
              </h3>
            )}
            {subtitle && (
              <p className="text-xs text-slate-400 mt-0.5">
                {subtitle}
              </p>
            )}
          </div>
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </div>
      )}

      {/* Content */}
      <div className="relative flex-1">{children}</div>
    </div>
  );
};
