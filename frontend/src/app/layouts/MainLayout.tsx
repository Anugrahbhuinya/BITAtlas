import { Outlet, useLocation, Link } from "react-router-dom";
import Sidebar from "../../shared/components/Sidebar";
import { useAuth } from "../../features/auth/hooks/useAuth";
import usePreferences from "../../features/preferences/hooks/usePreferences";
import { Sun, Moon, Monitor, User } from "lucide-react";

export function MainLayout() {
  const { currentUser } = useAuth();
  const { preferences, partialUpdatePreferences } = usePreferences();
  const location = useLocation();

  // Resolve dynamic title based on location pathname
  const getPageTitle = (path: string) => {
    if (path === "/") return "Dashboard";
    if (path.startsWith("/chat")) return "AI Assistant";
    if (path.startsWith("/notices")) return "Notices";
    if (path.startsWith("/academics")) return "Academics";
    if (path.startsWith("/map")) return "Campus Map";
    if (path.startsWith("/profile")) return "My Profile";
    return "BIT Mesra AI";
  };

  const title = getPageTitle(location.pathname);

  // Cycle: Light -> Dark -> System -> Light
  const cycleTheme = async () => {
    if (!preferences) return;
    const current = preferences.theme;
    const nextTheme: Record<string, "Light" | "Dark" | "System"> = {
      Light: "Dark",
      Dark: "System",
      System: "Light",
    };
    const target = nextTheme[current] || "System";
    try {
      await partialUpdatePreferences({ theme: target });
    } catch (e) {
      console.error("Failed to toggle theme", e);
    }
  };

  const getThemeIcon = () => {
    if (!preferences) return <Monitor size={15} />;
    switch (preferences.theme) {
      case "Light":
        return <Sun size={15} />;
      case "Dark":
        return <Moon size={15} />;
      case "System":
      default:
        return <Monitor size={15} />;
    }
  };

  return (
    <div className="h-screen w-screen flex bg-background overflow-hidden text-on-surface font-sans">
      {/* Left Navigation Sidebar */}
      <Sidebar />

      {/* Main Viewport Container */}
      <main className="flex-1 flex flex-col h-full overflow-hidden min-w-0 bg-background relative" role="main">
        {/* Top App Bar - Fixed height (never scrolls) */}
        <header className="flex justify-between items-center w-full h-16 px-6 bg-background border-b border-outline-variant/30 shrink-0 z-40 select-none">
          <div className="flex items-center gap-6">
            <h2 className="text-lg md:text-xl font-bold text-primary tracking-tight">{title}</h2>
            
            {/* Global Search Bar Shortcut */}
            <div 
              className="hidden lg:flex items-center gap-2 px-3.5 py-1.5 bg-surface-container-low border border-outline-variant rounded-xl w-60 select-none opacity-80 hover:opacity-100 hover:border-primary/50 transition-all cursor-pointer"
              title="Command search feature coming soon"
            >
              <span className="text-[10px] text-on-surface-variant/50 font-bold uppercase tracking-wider">Search workspace...</span>
              <kbd className="ml-auto bg-surface-container-high border border-outline-variant px-1 rounded text-[8px] font-mono font-bold text-on-surface-variant">⌘K</kbd>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Status Indicator */}
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-surface-container-low border border-outline-variant rounded-xl select-none">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" aria-hidden="true"></span>
              <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">AI Online</span>
            </div>

            {/* Notification Bell Shortcut */}
            <Link 
              to="/notices" 
              aria-label="View notifications and notices"
              className="p-2 hover:bg-surface-container-high rounded-xl text-on-surface-variant hover:text-primary transition-all relative cursor-pointer focus-visible:ring-1 focus-visible:ring-primary focus:outline-none"
            >
              <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-primary rounded-full" aria-hidden="true"></span>
              <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-bell"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
            </Link>

            {/* Theme Toggle Button */}
            {preferences && (
              <button
                onClick={cycleTheme}
                title={`Active Theme: ${preferences.theme}. Click to change.`}
                aria-label={`Toggle theme, current: ${preferences.theme}`}
                className="p-2 hover:bg-surface-container-high rounded-xl text-on-surface-variant hover:text-primary transition-all cursor-pointer focus-visible:ring-1 focus-visible:ring-primary focus:outline-none"
              >
                {getThemeIcon()}
              </button>
            )}

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
