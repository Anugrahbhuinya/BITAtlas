import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../features/auth/hooks/useAuth";
import { 
  LayoutDashboard, Bot, Bell, GraduationCap, 
  Map, User, LogOut, Plus, Menu 
} from "lucide-react";

interface SidebarProps {
  isCollapsed: boolean;
  isMobileOpen: boolean;
  setIsMobileOpen: (open: boolean) => void;
  onToggleCollapse: () => void;
}

const navGroups = [
  [
    {
      label: "Dashboard",
      icon: LayoutDashboard,
      path: "/",
    },
    {
      label: "AI Assistant",
      icon: Bot,
      path: "/chat",
    },
  ],
  [
    {
      label: "Academics",
      icon: GraduationCap,
      path: "/academics",
    },
    {
      label: "Campus Map",
      icon: Map,
      path: "/map",
    },
    {
      label: "Notices",
      icon: Bell,
      path: "/notices",
    },
  ],
  [
    {
      label: "Profile",
      icon: User,
      path: "/profile",
    },
  ],
];

export const Sidebar = ({ isCollapsed, isMobileOpen, setIsMobileOpen, onToggleCollapse }: SidebarProps) => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      setIsMobileOpen(false);
      navigate("/login");
    } catch (e) {
      console.error("Logout error", e);
    }
  };

  const handleNewChat = () => {
    setIsMobileOpen(false);
    navigate("/chat");
    window.location.reload(); // Simple direct reload clears active chat messages instantly!
  };

  return (
    <>
      {/* Mobile Drawer Overlay Backdrop */}
      {isMobileOpen && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-xs z-40 md:hidden transition-opacity duration-300"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Main Sidebar Component */}
      <aside 
        className={`
          fixed inset-y-0 left-0 z-50 flex flex-col py-6 bg-surface-container-low border-r border-outline-variant shrink-0 select-none transition-all duration-300 ease-in-out md:static md:translate-x-0 md:flex
          ${isCollapsed ? "md:w-16 w-60 md:px-0" : "md:w-60 w-60 px-0"}
          ${isMobileOpen ? "translate-x-0" : "-translate-x-full"}
        `}
      >
        {/* Brand Logo Header */}
        <div className={`px-5 mb-8 flex items-center justify-between transition-all duration-300 ${isCollapsed ? "md:px-0 md:justify-center md:flex-col md:gap-3" : "gap-3"}`}>
          {/* Logo and Text */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded bg-primary flex items-center justify-center text-background shrink-0">
              <GraduationCap size={20} className="fill-current text-background" />
            </div>
            <div className={`transition-all duration-300 ${isCollapsed ? "md:w-0 md:opacity-0 md:overflow-hidden" : "w-auto opacity-100"}`}>
              <h1 className="text-sm font-bold text-primary leading-tight whitespace-nowrap">BIT Mesra AI</h1>
              <p className="text-[10px] text-on-surface-variant font-medium tracking-wider uppercase opacity-65 whitespace-nowrap">Campus Assistant</p>
            </div>
          </div>

          {/* Toggle Hamburger inside Sidebar (desktop only) */}
          <button
            onClick={onToggleCollapse}
            aria-label="Collapse sidebar"
            className="hidden md:flex p-1.5 hover:bg-surface-container-high rounded-lg text-on-surface-variant hover:text-primary transition-all cursor-pointer focus-visible:ring-1 focus-visible:ring-primary focus:outline-none shrink-0"
          >
            <Menu size={16} />
          </button>
        </div>

        {/* New Chat Button */}
        <div className={`mb-6 transition-all duration-300 ${isCollapsed ? "md:px-2 md:text-center" : "px-4"}`}>
          <button 
            onClick={handleNewChat}
            className={`
              flex items-center justify-center bg-primary hover:bg-primary/95 text-background font-bold transition-all active:scale-[0.98] cursor-pointer shadow-md relative group/btn
              ${isCollapsed ? "md:w-10 md:h-10 md:p-0 md:rounded-full mx-auto" : "w-full gap-2 py-3 rounded-xl"}
            `}
            title={isCollapsed ? "New Chat" : undefined}
          >
            <Plus size={16} className="shrink-0" />
            <span className={`text-xs font-bold uppercase tracking-wider transition-all duration-300 ${isCollapsed ? "md:hidden" : "block"}`}>
              New Chat
            </span>
            {isCollapsed && (
              <span className="hidden md:block absolute left-full ml-4 px-2 py-1 bg-surface-container-highest text-on-surface text-[10px] rounded opacity-0 pointer-events-none group-hover/btn:opacity-100 transition-opacity whitespace-nowrap shadow-md z-50">
                New Chat
              </span>
            )}
          </button>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 space-y-4 px-2 overflow-y-auto custom-scrollbar">
          {navGroups.map((group, groupIdx) => (
            <div key={groupIdx} className="space-y-1">
              {groupIdx > 0 && <div className={`border-t border-outline-variant/20 my-3 transition-all duration-300 ${isCollapsed ? "md:mx-2" : "md:mx-4"}`} />}
              <div className="space-y-0.5">
                {group.map((item) => {
                  const Icon = item.icon;
                  return (
                    <NavLink
                      key={item.path}
                      to={item.path}
                      onClick={() => setIsMobileOpen(false)}
                      className={({ isActive }) =>
                        `flex items-center rounded-xl text-xs font-bold uppercase tracking-wider transition-all duration-150 relative group ${
                          isCollapsed 
                            ? "md:justify-center md:px-0 md:mx-1 md:h-10 md:w-10" 
                            : "gap-3 px-4 py-2.5"
                        } ${
                          isActive
                            ? "bg-surface-container-high text-primary border-l-2 border-primary"
                            : "text-on-surface-variant hover:text-primary hover:bg-surface-container/60"
                        }`
                      }
                    >
                      <Icon size={14} className="shrink-0 transition-transform group-hover:scale-105" />
                      <span className={`transition-all duration-300 ${isCollapsed ? "md:hidden" : "block"}`}>{item.label}</span>
                      {isCollapsed && (
                        <span className="hidden md:block absolute left-full ml-4 px-2 py-1 bg-surface-container-highest text-on-surface text-[10px] rounded opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity whitespace-nowrap shadow-md z-50">
                          {item.label}
                        </span>
                      )}
                    </NavLink>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Logout Action at Bottom */}
        <div className={`mt-auto pt-4 border-t border-outline-variant/30 ${isCollapsed ? "md:px-1" : "px-2"}`}>
          <button
            onClick={handleLogout}
            className={`
              flex items-center text-on-surface-variant hover:text-red-400 hover:bg-red-500/10 rounded-lg text-xs font-bold uppercase tracking-wider transition-colors cursor-pointer relative group/logout
              ${isCollapsed ? "md:justify-center md:px-0 md:h-10 md:w-10 md:mx-auto" : "w-full gap-3 px-4 py-3"}
            `}
          >
            <LogOut size={14} className="shrink-0" />
            <span className={`transition-all duration-300 ${isCollapsed ? "md:hidden" : "block"}`}>Logout</span>
            {isCollapsed && (
              <span className="hidden md:block absolute left-full ml-4 px-2 py-1 bg-surface-container-highest text-on-surface text-[10px] rounded opacity-0 pointer-events-none group-hover/logout:opacity-100 transition-opacity whitespace-nowrap shadow-md z-50">
                Logout
              </span>
            )}
          </button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
