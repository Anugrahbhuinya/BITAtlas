import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  description?: string;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  colorClass?: string;
  delay?: number;
}

export const StatsCard = ({
  title,
  value,
  icon: Icon,
  description,
  trend,
  colorClass = "bg-blue-500/10 text-blue-400 border-blue-500/20",
  delay = 0,
}: StatsCardProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      className="glass-panel p-6 rounded-2xl border border-slate-800/40 relative overflow-hidden flex flex-col justify-between"
    >
      {/* Subtle backdrop circle glow */}
      <div className="absolute top-0 right-0 -mr-6 -mt-6 w-24 h-24 bg-white/2 rounded-full blur-xl pointer-events-none" />

      <div className="flex justify-between items-start gap-4">
        <div>
          <span className="text-xs font-medium text-slate-400 tracking-wider uppercase">
            {title}
          </span>
          <h3 className="text-2xl font-bold text-slate-100 mt-2 tracking-tight">
            {value}
          </h3>
        </div>

        <div className={`p-2.5 rounded-xl border ${colorClass}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      {(trend || description) && (
        <div className="flex items-center gap-2 mt-4 pt-3 border-t border-slate-800/40 text-xs">
          {trend && (
            <span className={`font-semibold ${trend.isPositive ? "text-emerald-400" : "text-rose-400"}`}>
              {trend.value}
            </span>
          )}
          {description && (
            <span className="text-slate-400">
              {description}
            </span>
          )}
        </div>
      )}
    </motion.div>
  );
};
