import { useState } from "react";
import { Outlet, useLocation, Link } from "react-router-dom";
import { API_BASE_URL } from "../../config";
import Sidebar from "../../shared/components/Sidebar";
import { useAuth } from "../../features/auth/hooks/useAuth";
import { User, Menu } from "lucide-react";

export function MainLayout() {
  const { currentUser } = useAuth();
  const location = useLocation();

  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(() => {
    return localStorage.getItem("bit_mesra_sidebar_collapsed") === "true";
  });
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Resolve dynamic title based on location pathname
  const getPageTitle = (path: string) => {
    if (path === "/") return "Dashboard";
    if (path.startsWith("/chat")) return "AI Assistant";
    if (path.startsWith("/notices")) return "Notices";
    if (path.startsWith("/academics")) return "Academics";
    if (path.startsWith("/map")) return "Campus Map";
    if (path.startsWith("/profile")) return "My Profile";
    return "BITAtlas";
  };

  const title = getPageTitle(location.pathname);

  const toggleSidebar = () => {
    setIsSidebarCollapsed((prev) => {
      const next = !prev;
      localStorage.setItem("bit_mesra_sidebar_collapsed", String(next));
      return next;
    });
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen((prev) => !prev);
  };

  return (
    <div className="h-screen w-screen flex bg-background overflow-hidden text-on-surface font-sans">
      {/* Left Navigation Sidebar */}
      <Sidebar 
        isCollapsed={isSidebarCollapsed} 
        isMobileOpen={isMobileMenuOpen} 
        setIsMobileOpen={setIsMobileMenuOpen} 
        onToggleCollapse={toggleSidebar}
      />

      {/* Main Viewport Container */}
      <main className="flex-1 flex flex-col h-full overflow-hidden min-w-0 bg-background relative" role="main">
        {/* Top App Bar - Fixed height (never scrolls) */}
        <header className="flex justify-between items-center w-full h-16 px-6 bg-background border-b border-outline-variant/30 shrink-0 z-40 select-none">
          <div className="flex items-center gap-4">
            {/* Hamburger button for mobile menu trigger */}
            <button
              onClick={toggleMobileMenu}
              aria-label="Toggle sidebar mobile"
              className="flex md:hidden p-2 hover:bg-surface-container-high rounded-xl text-on-surface-variant hover:text-primary transition-all cursor-pointer focus-visible:ring-1 focus-visible:ring-primary focus:outline-none"
            >
              <Menu size={18} />
            </button>

            <h2 className="text-lg md:text-xl font-bold text-primary tracking-tight">{title}</h2>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Status Indicator */}
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-surface-container-low border border-outline-variant rounded-xl select-none">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" aria-hidden="true"></span>
              <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">AI Online</span>
            </div>

            {/* Profile Trigger Avatar */}
            {currentUser && (
              <Link 
                to="/profile" 
                aria-label="View student profile"
                title="View Profile"
                className="w-8 h-8 rounded-full overflow-hidden border border-outline-variant flex items-center justify-center cursor-pointer hover:border-primary transition-colors bg-surface-container-high shrink-0 focus-visible:ring-1 focus-visible:ring-primary focus:outline-none"
              >
                {currentUser.profile_picture ? (
                  <img 
                    src={`${API_BASE_URL}${currentUser.profile_picture}`} 
                    alt={currentUser.name} 
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <User size={14} className="text-primary" />
                )}
              </Link>
            )}
          </div>
        </header>

        {/* Dynamic Page Viewport Canvas - overflow-hidden to prevent nested scrollbars */}
        <div className="flex-1 overflow-hidden min-h-0 bg-background">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

export default MainLayout;
