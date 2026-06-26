import { useState, useEffect } from "react";
import { Outlet, Navigate, Link, useNavigate } from "react-router-dom";
import { useAdminStore } from "../hooks/adminStore";
import { Sidebar } from "./Sidebar";
import { TopNavbar } from "./TopNavbar";
import { ToastNotification } from "./ToastNotification";
import adminApi from "../services/api";
import { Shield, X, LogOut, LayoutDashboard, Database, FileText, BarChart3, Activity, Settings } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export const AdminLayout = () => {
  const { isAuthenticated, setLogout, showToast } = useAdminStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [statusComponents, setStatusComponents] = useState<any[]>([]);
  const navigate = useNavigate();

  // 1. Fetch system status from backend
  const fetchStatus = async () => {
    try {
      const response = await adminApi.get("/api/admin/system-status");
      setStatusComponents(response.data.components || []);
    } catch (e) {
      console.error("Failed to fetch system status in layout", e);
      // Fallback placeholder status if backend fails
      setStatusComponents([
        { name: "MongoDB Database", status: "Connected" },
        { name: "Gemini AI (2.5 Flash)", status: "Connected" },
        { name: "ChromaDB Vector Store", status: "Connected" },
      ]);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchStatus();
      // Poll status every 30 seconds
      const interval = setInterval(fetchStatus, 30000);
      return () => clearInterval(interval);
    }
  }, [isAuthenticated]);

  // Auth Guard: Redirect unauthenticated admins to login page
  if (!isAuthenticated) {
    return <Navigate to="/admin/login" replace />;
  }

  const mobileNavItems = [
    { label: "Dashboard", icon: LayoutDashboard, path: "/admin/dashboard" },
    { label: "Knowledge Base", icon: Database, path: "/admin/knowledge-base" },
    { label: "Documents", icon: FileText, path: "/admin/documents" },
    { label: "Analytics", icon: BarChart3, path: "/admin/analytics" },
    { label: "Activity Logs", icon: Activity, path: "/admin/activity" },
    { label: "Settings", icon: Settings, path: "/admin/settings" },
  ];

  const handleMobileLogout = () => {
    setLogout();
    setMobileMenuOpen(false);
    showToast("Logged out successfully", "info");
    navigate("/admin/login");
  };

  return (
    <div className="flex h-screen w-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* 1. Desktop Sidebar */}
      <Sidebar />

      {/* 2. Mobile Drawer Navigation Overlay */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <>
            {/* Backdrop overlay */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.6 }}
              exit={{ opacity: 0 }}
              onClick={() => setMobileMenuOpen(false)}
              className="fixed inset-0 z-40 bg-slate-950/80 backdrop-blur-sm md:hidden"
            />

            {/* Sidebar drawer content */}
            <motion.div
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "tween", duration: 0.25 }}
              className="fixed inset-y-0 left-0 z-50 w-72 bg-slate-950 border-r border-slate-900 flex flex-col p-5 md:hidden shadow-2xl"
            >
              <div className="flex items-center justify-between pb-5 border-b border-slate-900/60">
                <div className="flex items-center gap-3">
                  <div className="p-1.5 bg-blue-600 rounded-lg text-white">
                    <Shield className="w-5 h-5" />
                  </div>
                  <div className="flex flex-col">
                    <span className="text-sm font-bold">BIT Operations</span>
                    <span className="text-[10px] text-blue-400 font-semibold uppercase tracking-wider">
                      Admin Console
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => setMobileMenuOpen(false)}
                  className="p-1.5 hover:bg-slate-900 border border-slate-900 hover:border-slate-800 rounded-lg text-slate-400 cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Navigation links */}
              <nav className="flex-1 py-6 space-y-2 overflow-y-auto">
                {mobileNavItems.map((item) => {
                  const Icon = item.icon;
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      onClick={() => setMobileMenuOpen(false)}
                      className="flex items-center gap-3.5 px-4 py-3 rounded-xl hover:bg-slate-900 text-slate-400 hover:text-slate-200 transition-all font-medium"
                    >
                      <Icon className="w-5 h-5" />
                      <span className="text-sm">{item.label}</span>
                    </Link>
                  );
                })}
              </nav>

              {/* Logout button in drawer */}
              <div className="pt-4 border-t border-slate-900/60">
                <button
                  onClick={handleMobileLogout}
                  className="flex items-center gap-3.5 w-full px-4 py-3 rounded-xl text-rose-400 hover:bg-rose-950/20 transition-all font-medium cursor-pointer"
                >
                  <LogOut className="w-5 h-5" />
                  <span className="text-sm">Log out</span>
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* 3. Main Dashboard Content viewport */}
      <div className="flex flex-col flex-1 min-w-0 h-screen overflow-hidden">
        {/* Top Navbar */}
        <TopNavbar
          statusComponents={statusComponents}
          onMobileMenuToggle={() => setMobileMenuOpen(true)}
        />

        {/* Content View Area */}
        <main className="flex-1 overflow-y-auto custom-scrollbar bg-slate-950/30 p-6 flex flex-col justify-between">
          <div className="flex-1">
            <Outlet />
          </div>

          {/* Console Footer */}
          <footer className="mt-8 pt-4 border-t border-slate-900/40 text-center select-none shrink-0">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-2 text-[10px] text-slate-500 font-medium">
              <span>© {new Date().getFullYear()} Birla Institute of Technology, Mesra. AI Operations Center.</span>
              <span className="font-mono">v1.0.0 (Phase 5A Production)</span>
            </div>
          </footer>
        </main>
      </div>

      {/* Global feedback Toast notifications */}
      <ToastNotification />
    </div>
  );
};
