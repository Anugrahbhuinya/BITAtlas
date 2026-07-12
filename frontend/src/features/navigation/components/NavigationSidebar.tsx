// src/features/navigation/components/NavigationSidebar.tsx

import React, { useState } from "react";
import { 
  ChevronDown, ChevronUp, Star, Compass, History, Navigation, Map, Layers, Search
} from "lucide-react";
import QuickDestinations from "./QuickDestinations";
import FavoritesPanel from "./FavoritesPanel";
import RecentLocations from "./RecentLocations";
import NearbyPlaces from "./NearbyPlaces";
import NavigationSearch from "./NavigationSearch";
import type { Building, Facility, Landmark as LandmarkType, NavigationSearchResult } from "../types";

interface NavigationSidebarProps {
  // Datasets
  allNodes: any[];
  buildings: Building[];
  facilities: Facility[];
  landmarks: LandmarkType[];

  // Search callbacks
  onResultSelect: (result: NavigationSearchResult) => void;
  onClearSearch: () => void;

  // Favorites state & actions
  favorites: any[];
  onSelectFavorite: (fav: any) => void;
  onNavigateFavorite: (fav: any) => void;
  onRemoveFavorite: (id: string) => void;

  // Recents state & actions
  recents: any[];
  onSelectRecent: (rec: any) => void;
  onNavigateRecent: (rec: any) => void;
  onClearRecents: () => void;

  // Quick destinations callback
  onQuickDestinationSelect: (id: string, name: string) => void;

  // Nearby callbacks
  selectedEntity: any | null;
  onSelectNearby: (entity: any, type: "building" | "facility" | "landmark") => void;
  onNavigateNearby: (entity: any, name: string) => void;

  // Layers toggle
  onToggleLayers: () => void;

  // Routing panel slot (we pass the existing RoutePanel as children or render it inside)
  isRouting: boolean;
  routePanelElement: React.ReactNode;
}

export const NavigationSidebar: React.FC<NavigationSidebarProps> = ({
  allNodes,
  buildings,
  facilities,
  landmarks,
  onResultSelect,
  onClearSearch,
  favorites,
  onSelectFavorite,
  onNavigateFavorite,
  onRemoveFavorite,
  recents,
  onSelectRecent,
  onNavigateRecent,
  onClearRecents,
  onQuickDestinationSelect,
  selectedEntity,
  onSelectNearby,
  onNavigateNearby,
  onToggleLayers,
  isRouting,
  routePanelElement
}) => {
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({
    search: false,
    quick: false,
    favorites: false,
    recents: true,
    nearby: false
  });

  const toggleSection = (section: string) => {
    setCollapsed((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  return (
    <div className="bg-surface/90 border border-outline-variant/65 rounded-3xl p-5 shadow-2xl backdrop-blur-md flex flex-col gap-4 max-h-[85vh] overflow-y-auto w-full max-w-sm text-left select-none relative z-[1000] custom-scrollbar">
      {/* Search Section */}
      <div className="space-y-2">
        <NavigationSearch
          onResultSelect={onResultSelect}
          onClear={onClearSearch}
        />
      </div>

      {/* Layer Control Toggle Button */}
      <button
        onClick={onToggleLayers}
        className="w-full py-2 px-3 border border-outline-variant/50 hover:bg-surface-variant/35 rounded-2xl flex items-center justify-between text-xs font-bold text-on-surface/85 transition"
      >
        <span className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-primary" />
          Customize Map Layers & Legend
        </span>
        <Map className="w-3.5 h-3.5 opacity-55" />
      </button>

      {/* Active Routing Panel */}
      {isRouting && (
        <div className="border-t border-outline-variant/35 pt-4">
          {routePanelElement}
        </div>
      )}

      {/* Collapsible: Quick Destinations */}
      <div className="border border-outline-variant/35 rounded-2xl overflow-hidden bg-surface-variant/10">
        <button
          onClick={() => toggleSection("quick")}
          className="w-full p-3 bg-surface-variant/20 flex justify-between items-center text-[10px] font-black text-on-surface/65 uppercase tracking-wider hover:bg-surface-variant/30 transition"
        >
          <span className="flex items-center gap-1.5">
            <Compass className="w-3.5 h-3.5 text-primary" />
            Quick Destinations
          </span>
          {collapsed.quick ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
        </button>
        {!collapsed.quick && (
          <div className="p-3.5 border-t border-outline-variant/35 bg-surface/20">
            <QuickDestinations onSelect={onQuickDestinationSelect} />
          </div>
        )}
      </div>

      {/* Collapsible: Favorites */}
      <div className="border border-outline-variant/35 rounded-2xl overflow-hidden bg-surface-variant/10">
        <button
          onClick={() => toggleSection("favorites")}
          className="w-full p-3 bg-surface-variant/20 flex justify-between items-center text-[10px] font-black text-on-surface/65 uppercase tracking-wider hover:bg-surface-variant/30 transition"
        >
          <span className="flex items-center gap-1.5">
            <Star className="w-3.5 h-3.5 text-amber-400" />
            Favorites ({favorites.length})
          </span>
          {collapsed.favorites ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
        </button>
        {!collapsed.favorites && (
          <div className="p-3.5 border-t border-outline-variant/35 bg-surface/20">
            <FavoritesPanel
              favorites={favorites}
              onSelect={onSelectFavorite}
              onNavigate={onNavigateFavorite}
              onRemove={onRemoveFavorite}
            />
          </div>
        )}
      </div>

      {/* Collapsible: Recent History */}
      <div className="border border-outline-variant/35 rounded-2xl overflow-hidden bg-surface-variant/10">
        <button
          onClick={() => toggleSection("recents")}
          className="w-full p-3 bg-surface-variant/20 flex justify-between items-center text-[10px] font-black text-on-surface/65 uppercase tracking-wider hover:bg-surface-variant/30 transition"
        >
          <span className="flex items-center gap-1.5">
            <History className="w-3.5 h-3.5 text-on-surface/40" />
            Recently Visited ({recents.length})
          </span>
          {collapsed.recents ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
        </button>
        {!collapsed.recents && (
          <div className="p-3.5 border-t border-outline-variant/35 bg-surface/20">
            <RecentLocations
              recents={recents}
              onSelect={onSelectRecent}
              onNavigate={onNavigateRecent}
              onClearAll={onClearRecents}
            />
          </div>
        )}
      </div>

      {/* Collapsible: Nearby Places */}
      <div className="border border-outline-variant/35 rounded-2xl overflow-hidden bg-surface-variant/10">
        <button
          onClick={() => toggleSection("nearby")}
          className="w-full p-3 bg-surface-variant/20 flex justify-between items-center text-[10px] font-black text-on-surface/65 uppercase tracking-wider hover:bg-surface-variant/30 transition"
        >
          <span className="flex items-center gap-1.5">
            <Navigation className="w-3.5 h-3.5 text-primary rotate-45" />
            Explore Nearby Services
          </span>
          {collapsed.nearby ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
        </button>
        {!collapsed.nearby && (
          <div className="p-3.5 border-t border-outline-variant/35 bg-surface/20">
            <NearbyPlaces
              selectedEntity={selectedEntity}
              buildings={buildings}
              facilities={facilities}
              landmarks={landmarks}
              onSelect={onSelectNearby}
              onNavigate={onNavigateNearby}
            />
          </div>
        )}
      </div>
    </div>
  );
};
export default NavigationSidebar;
