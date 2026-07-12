// src/features/navigation/components/LayersDrawer.tsx

import React, { useState, useEffect } from "react";
import { X, Search, RotateCcw, ShieldAlert, Sliders, CheckSquare, Square, Eye, EyeOff } from "lucide-react";
import type { Building, Facility, Landmark } from "../types";

interface LayersDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  
  // Layer visibility states & setters
  showBuildings: boolean;
  setShowBuildings: (show: boolean) => void;
  showLandmarks: boolean;
  setShowLandmarks: (show: boolean) => void;
  showFacilities: boolean;
  setShowFacilities: (show: boolean) => void;
  showRouteLayer: boolean;
  setShowRouteLayer: (show: boolean) => void;

  // Datasets for category counts
  buildings: Building[];
  landmarks: Landmark[];
  facilities: Facility[];
  routeActive: boolean;
}

export const LayersDrawer: React.FC<LayersDrawerProps> = ({
  isOpen,
  onClose,
  showBuildings,
  setShowBuildings,
  showLandmarks,
  setShowLandmarks,
  showFacilities,
  setShowFacilities,
  showRouteLayer,
  setShowRouteLayer,
  buildings,
  landmarks,
  facilities,
  routeActive
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [collapsedSections, setCollapsedSections] = useState<Record<string, boolean>>({
    visibility: false,
    legend: false
  });

  // ESC key handler to close drawer
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  // Category statistics counts
  const countAcademic = buildings.filter(b => b.category === "Academic").length;
  const countAdmin = buildings.filter(b => b.category === "Administrative").length;
  const countHostels = buildings.filter(b => b.category === "Residential").length;
  const countFacilities = facilities.length;
  const countLandmarks = landmarks.length;

  const toggleCollapse = (section: string) => {
    setCollapsedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const handleResetFilters = () => {
    setShowBuildings(true);
    setShowLandmarks(true);
    setShowFacilities(true);
    setShowRouteLayer(true);
    setSearchQuery("");
  };

  const handleToggleAll = (val: boolean) => {
    setShowBuildings(val);
    setShowLandmarks(val);
    setShowFacilities(val);
    setShowRouteLayer(val);
  };

  return (
    <div className="fixed inset-y-0 right-0 z-[5000] w-full max-w-xs md:max-w-sm bg-surface/95 border-l border-outline-variant/60 shadow-2xl backdrop-blur-xl flex flex-col transition-all duration-300 ease-out p-6 text-left">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-outline-variant/35 pb-3 mb-4">
        <div className="flex items-center gap-2 text-primary">
          <Sliders className="w-4 h-4" />
          <h3 className="text-sm font-black tracking-tight">Map Settings & Layers</h3>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-full hover:bg-surface-variant text-on-surface/40 hover:text-on-surface transition"
          aria-label="Close settings drawer"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Search Input for categories/counts */}
      <div className="relative mb-4">
        <Search className="absolute left-3 top-2.5 w-3.5 h-3.5 text-on-surface/30" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Filter map categories..."
          className="w-full pl-9 pr-4 py-2 bg-surface-variant/40 hover:bg-surface-variant/75 border border-outline-variant/50 rounded-xl text-xs focus:outline-none focus:border-primary transition"
        />
      </div>

      {/* Global Toolbar buttons */}
      <div className="grid grid-cols-2 gap-2 mb-6">
        <button
          onClick={handleResetFilters}
          className="py-2 px-3 border border-outline-variant/65 rounded-xl text-[10px] font-bold hover:bg-surface-variant/30 flex items-center justify-center gap-1.5 transition text-on-surface/75"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Reset Settings
        </button>
        <button
          onClick={() => handleToggleAll(true)}
          className="py-2 px-3 border border-outline-variant/65 rounded-xl text-[10px] font-bold hover:bg-surface-variant/30 flex items-center justify-center gap-1.5 transition text-on-surface/75"
        >
          <Eye className="w-3.5 h-3.5" />
          Show All Layers
        </button>
      </div>

      {/* Collapsible Content Panels */}
      <div className="flex-1 overflow-y-auto space-y-5 pr-1 custom-scrollbar">
        {/* Layer Visibility Section */}
        <div className="border border-outline-variant/35 rounded-2xl overflow-hidden bg-surface-variant/10">
          <button
            onClick={() => toggleCollapse("visibility")}
            className="w-full p-3 bg-surface-variant/20 flex justify-between items-center text-xs font-black text-on-surface hover:bg-surface-variant/30 transition"
          >
            <span>Layer Visibility Controls</span>
            <span className="text-[10px] font-medium opacity-50">{collapsedSections.visibility ? "Expand" : "Collapse"}</span>
          </button>
          
          {!collapsedSections.visibility && (
            <div className="p-3.5 space-y-3.5 border-t border-outline-variant/35">
              {/* Buildings */}
              <label className="flex justify-between items-center cursor-pointer select-none text-xs font-bold text-on-surface/80">
                <span className="flex items-center gap-2">
                  <CheckSquare className={`w-4 h-4 text-primary transition ${showBuildings ? "opacity-100" : "opacity-35"}`} />
                  Academic & Administrative Blocks
                </span>
                <span className="text-[10px] opacity-40 font-mono">({countAcademic + countAdmin})</span>
                <input
                  type="checkbox"
                  checked={showBuildings}
                  onChange={(e) => setShowBuildings(e.target.checked)}
                  className="sr-only"
                />
              </label>

              {/* Hostels */}
              <label className="flex justify-between items-center cursor-pointer select-none text-xs font-bold text-on-surface/80">
                <span className="flex items-center gap-2">
                  <CheckSquare className={`w-4 h-4 text-primary transition ${showBuildings ? "opacity-100" : "opacity-35"}`} />
                  Residential Hostels
                </span>
                <span className="text-[10px] opacity-40 font-mono">({countHostels})</span>
                <input
                  type="checkbox"
                  checked={showBuildings}
                  onChange={(e) => setShowBuildings(e.target.checked)}
                  className="sr-only"
                />
              </label>

              {/* Facilities */}
              <label className="flex justify-between items-center cursor-pointer select-none text-xs font-bold text-on-surface/80">
                <span className="flex items-center gap-2">
                  <CheckSquare className={`w-4 h-4 text-primary transition ${showFacilities ? "opacity-100" : "opacity-35"}`} />
                  Campus Facilities (ATM/Cafe/etc)
                </span>
                <span className="text-[10px] opacity-40 font-mono">({countFacilities})</span>
                <input
                  type="checkbox"
                  checked={showFacilities}
                  onChange={(e) => setShowFacilities(e.target.checked)}
                  className="sr-only"
                />
              </label>

              {/* Landmarks */}
              <label className="flex justify-between items-center cursor-pointer select-none text-xs font-bold text-on-surface/80">
                <span className="flex items-center gap-2">
                  <CheckSquare className={`w-4 h-4 text-primary transition ${showLandmarks ? "opacity-100" : "opacity-35"}`} />
                  Key Landmarks & POIs
                </span>
                <span className="text-[10px] opacity-40 font-mono">({countLandmarks})</span>
                <input
                  type="checkbox"
                  checked={showLandmarks}
                  onChange={(e) => setShowLandmarks(e.target.checked)}
                  className="sr-only"
                />
              </label>

              {/* Route Polyline Layer */}
              {routeActive && (
                <label className="flex justify-between items-center cursor-pointer select-none text-xs font-bold text-on-surface/80 border-t border-outline-variant/35 pt-3">
                  <span className="flex items-center gap-2">
                    <CheckSquare className={`w-4 h-4 text-primary transition ${showRouteLayer ? "opacity-100" : "opacity-35"}`} />
                    Active Navigation Route Polyline
                  </span>
                  <input
                    type="checkbox"
                    checked={showRouteLayer}
                    onChange={(e) => setShowRouteLayer(e.target.checked)}
                    className="sr-only"
                  />
                </label>
              )}
            </div>
          )}
        </div>

        {/* Map Colors Legend */}
        <div className="border border-outline-variant/35 rounded-2xl overflow-hidden bg-surface-variant/10">
          <button
            onClick={() => toggleCollapse("legend")}
            className="w-full p-3 bg-surface-variant/20 flex justify-between items-center text-xs font-black text-on-surface hover:bg-surface-variant/30 transition"
          >
            <span>Map Colors Legend</span>
            <span className="text-[10px] font-medium opacity-50">{collapsedSections.legend ? "Expand" : "Collapse"}</span>
          </button>
          
          {!collapsedSections.legend && (
            <div className="p-3.5 space-y-3.5 border-t border-outline-variant/35">
              <div className="flex items-center gap-2.5 text-xs font-semibold text-on-surface/80">
                <span className="w-3.5 h-3.5 rounded-full bg-blue-500 flex-shrink-0" />
                <span>Academic Blocks</span>
              </div>
              <div className="flex items-center gap-2.5 text-xs font-semibold text-on-surface/80">
                <span className="w-3.5 h-3.5 rounded-full bg-purple-500 flex-shrink-0" />
                <span>Administrative offices</span>
              </div>
              <div className="flex items-center gap-2.5 text-xs font-semibold text-on-surface/80">
                <span className="w-3.5 h-3.5 rounded-full bg-emerald-500 flex-shrink-0" />
                <span>Student Hostels</span>
              </div>
              <div className="flex items-center gap-2.5 text-xs font-semibold text-on-surface/80">
                <span className="w-3.5 h-3.5 rounded-full bg-amber-500 flex-shrink-0" />
                <span>Landmarks & Statues</span>
              </div>
              <div className="flex items-center gap-2.5 text-xs font-semibold text-on-surface/80">
                <span className="w-3.5 h-3.5 rounded-full bg-orange-500 flex-shrink-0" />
                <span>Facilities (OPD/SBI/Nescafe)</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
export default LayersDrawer;
