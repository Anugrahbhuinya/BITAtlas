import { NavLink, useNavigate } from "react-router-dom";
import { useAdminStore } from "../hooks/adminStore";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  Database,
  FileText,
  BarChart3,
  Activity,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Shield,
} from "lucide-react";

interface SidebarProps {
  onMobileClose?: () => void;
}

export const Sidebar = ({ onMobileClose }: SidebarProps) => {
  const { sidebarCollapsed, toggleSidebar, setLogout, showToast } = useAdminStore();
  const navigate = useNavigate();

  const menuItems = [
    {
      label: "Dashboard",
      icon: LayoutDashboard,
      path: "/admin/dashboard",
    },
    {
      label: "Knowledge Base",
      icon: Database,
      path: "/admin/knowledge-base",
    },
    {
      label: "Documents",
      icon: FileText,
      path: "/admin/documents",
    },
    {
      label: "Analytics",
      icon: BarChart3,
      path: "/admin/analytics",
    },
    {
      label: "Activity",
      icon: Activity,
      path: "/admin/activity",
    },
    {
      label: "Settings",
      icon: Settings,
      path: "/admin/settings",
    },
  ];

  const handleLogout = () => {
    setLogout();
    showToast("Logged out successfully", "info");
    navigate("/admin/login");
    if (onMobileClose) onMobileClose();
  };

  const containerVariants = {
    expanded: { width: "256px" },
    collapsed: { width: "80px" },
  };

  return (
    <motion.aside
      initial={sidebarCollapsed ? "collapsed" : "expanded"}
      animate={sidebarCollapsed ? "collapsed" : "expanded"}
      variants={containerVariants}
      transition={{ duration: 0.3, ease: "easeInOut" }}
      className="hidden md:flex flex-col h-screen bg-slate-950 border-r border-slate-900 sticky top-0 overflow-y-auto overflow-x-hidden custom-scrollbar shrink-0"
    >
      {/* Brand logo header */}
      <div className="flex items-center justify-between p-5 border-b border-slate-900/60 min-h-[73px]">
        <div className="flex items-center gap-3">
          <div className="p-1.5 bg-blue-600 rounded-lg text-white glow-blue shadow-lg">
            <Shield className="w-5 h-5" />
          </div>
          {!sidebarCollapsed && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0 }}
              className="flex flex-col"
            >
              <span className="text-sm font-bold text-slate-100 whitespace-nowrap">
                BIT Operations
              </span>
              <span className="text-[10px] text-blue-400 font-semibold tracking-wider uppercase">
                Admin Console
              </span>
            </motion.div>
          )}
        </div>

        {/* Collapsing button */}
        {!sidebarCollapsed && (
          <button
            onClick={toggleSidebar}
            className="p-1 hover:bg-slate-900 rounded-lg border border-slate-900 hover:border-slate-800 text-slate-400 hover:text-slate-200 transition-all cursor-pointer"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Navigation menu list */}
      <nav className="flex-1 px-4 py-5 space-y-1.5">
        {menuItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3.5 px-3.5 py-3 rounded-xl transition-all duration-200 relative group cursor-pointer ${
                  isActive
                    ? "bg-blue-600/10 border-l-[3px] border-blue-500 text-blue-400 font-medium"
                    : "text-slate-400 hover:bg-slate-900/60 hover:text-slate-200 border-l-[3px] border-transparent"
                }`
              }
            >
              <Icon className="w-5 h-5 shrink-0" />
              {!sidebarCollapsed && (
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-sm whitespace-nowrap"
                >
                  {item.label}
                </motion.span>
              )}

              {/* Tooltip for collapsed states */}
              {sidebarCollapsed && (
                <div className="absolute left-16 scale-0 group-hover:scale-100 bg-slate-950 border border-slate-800 text-xs px-2.5 py-1.5 rounded-lg text-slate-200 whitespace-nowrap glow-blue transition-all z-20 pointer-events-none duration-150 origin-left">
                  {item.label}
                </div>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Collapse open button (only shown when collapsed) */}
      {sidebarCollapsed && (
        <div className="px-4 py-2 flex justify-center border-t border-slate-900/60">
          <button
            onClick={toggleSidebar}
            className="p-1.5 bg-slate-900 hover:bg-slate-800 rounded-lg border border-slate-800 text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Footer logout area */}
      <div className="p-4 border-t border-slate-900/60">
        <button
          onClick={handleLogout}
          className="flex items-center gap-3.5 w-full px-3.5 py-3 rounded-xl text-rose-400 hover:bg-rose-950/20 hover:text-rose-300 border-l-[3px] border-transparent transition-all duration-200 cursor-pointer group relative"
        >
          <LogOut className="w-5 h-5 shrink-0" />
          {!sidebarCollapsed && <span className="text-sm font-medium">Log out</span>}
          {sidebarCollapsed && (
            <div className="absolute left-16 scale-0 group-hover:scale-100 bg-slate-950 border border-rose-950/80 text-xs px-2.5 py-1.5 rounded-lg text-rose-300 whitespace-nowrap transition-all z-20 pointer-events-none duration-150 origin-left">
              Log out
            </div>
          )}
        </button>
      </div>
    </motion.aside>
  );
};
