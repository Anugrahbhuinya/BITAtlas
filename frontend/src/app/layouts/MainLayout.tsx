import { Outlet, useLocation, Link } from "react-router-dom";
import Sidebar from "../../shared/components/Sidebar";
import { useAuth } from "../../features/auth/hooks/useAuth";
import { User } from "lucide-react";

export function MainLayout() {
  const { currentUser } = useAuth();
  const location = useLocation();

  // Resolve dynamic title based on location pathname
  const getPageTitle = (path: string) => {
    if (path === "/") return "Dashboard";
    if (path.startsWith("/chat")) return "AI Assistant";
    if (path.startsWith("/notices")) return "Notices";
    if (path.startsWith("/academics")) return "Academics";
    if (path.startsWith("/map")) return "Campus Map";
    if (path.startsWith("/profile")) return "My Profile";
    if (path.startsWith("/settings")) return "Settings";
    return "BIT Mesra AI";
  };

  const title = getPageTitle(location.pathname);

  return (
    <div className="h-screen w-screen flex bg-background overflow-hidden text-on-surface font-sans">
      {/* Left Navigation Sidebar */}
      <Sidebar />

      {/* Main Viewport Container */}
      <main className="flex-1 flex flex-col h-full overflow-hidden min-w-0 bg-background relative">
        {/* Top App Bar - Fixed height (never scrolls) */}
        <header className="flex justify-between items-center w-full h-16 px-6 bg-background border-b border-outline-variant/30 shrink-0 z-40">
          <div className="flex items-center gap-4">
            <h2 className="text-lg md:text-xl font-bold text-primary tracking-tight">{title}</h2>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Status Indicator */}
            <div className="hidden md:flex items-center gap-2 px-3 py-1 bg-surface-container-low border border-outline-variant rounded-full">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">AI Online</span>
            </div>

            {/* Profile Trigger Avatar */}
            {currentUser && (
              <Link 
                to="/profile" 
                title="View Profile"
                className="w-8 h-8 rounded-full overflow-hidden border border-outline-variant flex items-center justify-center cursor-pointer hover:border-primary transition-colors bg-surface-container-high shrink-0"
              >
                {currentUser.profile_picture ? (
                  <img 
                    src={`http://localhost:8000${currentUser.profile_picture}`} 
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
