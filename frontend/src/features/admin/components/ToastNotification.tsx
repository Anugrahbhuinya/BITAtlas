import { motion, AnimatePresence } from "framer-motion";
import { useAdminStore } from "../hooks/adminStore";
import { CheckCircle2, AlertTriangle, Info, X } from "lucide-react";

export const ToastNotification = () => {
  const { toast, clearToast } = useAdminStore();

  if (!toast) return null;

  const icons = {
    success: <CheckCircle2 className="w-5 h-5 text-emerald-400" />,
    error: <AlertTriangle className="w-5 h-5 text-rose-400" />,
    info: <Info className="w-5 h-5 text-blue-400" />,
  };

  const bgColors = {
    success: "border-emerald-500/30 bg-emerald-950/40 text-emerald-100",
    error: "border-rose-500/30 bg-rose-950/40 text-rose-100",
    info: "border-blue-500/30 bg-blue-950/40 text-blue-100",
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 pointer-events-none">
      <AnimatePresence>
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -20, scale: 0.95 }}
          transition={{ duration: 0.2 }}
          className={`flex items-center gap-3 px-4 py-3 rounded-xl border backdrop-blur-xl shadow-2xl pointer-events-auto ${bgColors[toast.type]}`}
        >
          {icons[toast.type]}
          <span className="text-sm font-medium pr-2">{toast.message}</span>
          <button
            onClick={clearToast}
            className="p-1 hover:bg-white/10 rounded-lg transition-colors cursor-pointer"
          >
            <X className="w-4 h-4 opacity-70 hover:opacity-100" />
          </button>
        </motion.div>
      </AnimatePresence>
    </div>
  );
};
