import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import type { LucideIcon } from "lucide-react";
import { ArrowUpRight } from "lucide-react";

interface QuickActionCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
  to: string;
  colorClass?: string;
  delay?: number;
}

export const QuickActionCard = ({
  title,
  description,
  icon: Icon,
  to,
  colorClass = "bg-blue-500/10 border-blue-500/20 text-blue-400 group-hover:bg-blue-500/25",
  delay = 0,
}: QuickActionCardProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay }}
      whileHover={{ y: -3 }}
      className="group relative"
    >
      <Link
        to={to}
        className="block glass-panel p-5 rounded-2xl border border-slate-800/40 hover:border-slate-700/60 transition-all duration-300 relative overflow-hidden"
      >
        {/* Glow overlay */}
        <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-transparent to-white/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />

        <div className="flex items-start gap-4">
          <div className={`p-3 rounded-xl border transition-all duration-300 ${colorClass}`}>
            <Icon className="w-5 h-5" />
          </div>

          <div className="flex-1 min-w-0 pr-4">
            <h4 className="text-sm font-semibold text-slate-200 group-hover:text-white transition-colors">
              {title}
            </h4>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              {description}
            </p>
          </div>

          <div className="p-1 rounded-lg bg-slate-900 group-hover:bg-slate-800 border border-slate-800 text-slate-400 group-hover:text-slate-200 transition-all self-start">
            <ArrowUpRight className="w-3.5 h-3.5" />
          </div>
        </div>
      </Link>
    </motion.div>
  );
};
