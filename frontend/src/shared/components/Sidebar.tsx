import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../features/auth/hooks/useAuth";
import { 
  LayoutDashboard, Bot, Bell, GraduationCap, 
  Map, User, LogOut, Plus 
} from "lucide-react";

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

export const Sidebar = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/login");
    } catch (e) {
      console.error("Logout error", e);
    }
  };

  const handleNewChat = () => {
    // Navigate to chat and reload or dispatch start session if needed
    navigate("/chat");
    window.location.reload(); // Simple direct reload clears active chat messages instantly!
  };

  return (
    <aside className="hidden md:flex h-full w-[280px] bg-surface-container-low border-r border-outline-variant flex-col py-6 shrink-0 select-none">
      {/* Brand Logo Header */}
      <div className="px-6 mb-8 flex items-center gap-3">
        <div className="w-9 h-9 rounded bg-primary flex items-center justify-center text-background">
          <GraduationCap size={20} className="fill-current text-background" />
        </div>
        <div>
          <h1 className="text-sm md:text-base font-bold text-primary leading-tight">BIT Mesra AI</h1>
          <p className="text-[10px] text-on-surface-variant font-medium tracking-wider uppercase opacity-65">Campus Assistant</p>
        </div>
      </div>

      {/* New Chat Button */}
      <div className="px-4 mb-6">
        <button 
          onClick={handleNewChat}
          className="w-full flex items-center justify-center gap-2 py-3 bg-primary hover:bg-primary/95 text-background rounded-xl font-bold transition-all active:scale-[0.98] cursor-pointer shadow-md"
        >
          <Plus size={16} />
          <span className="text-xs font-bold uppercase tracking-wider">New Chat</span>
        </button>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 space-y-4 px-2 overflow-y-auto custom-scrollbar">
        {navGroups.map((group, groupIdx) => (
          <div key={groupIdx} className="space-y-1">
            {groupIdx > 0 && <div className="border-t border-outline-variant/20 my-3 mx-4" />}
            <div className="space-y-0.5">
              {group.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-4 py-2.5 rounded-xl text-xs font-bold uppercase tracking-wider transition-all duration-150 relative group ${
                        isActive
                          ? "bg-surface-container-high text-primary border-l-2 border-primary"
                          : "text-on-surface-variant hover:text-primary hover:bg-surface-container/60"
                      }`
                    }
                  >
                    <Icon size={14} className="shrink-0 transition-transform group-hover:scale-105" />
                    <span>{item.label}</span>
                  </NavLink>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Logout Action at Bottom */}
      <div className="px-2 mt-auto pt-4 border-t border-outline-variant/30">
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-3 text-on-surface-variant hover:text-red-400 hover:bg-red-500/10 rounded-lg text-xs font-bold uppercase tracking-wider transition-colors cursor-pointer"
        >
          <LogOut size={14} className="shrink-0" />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
