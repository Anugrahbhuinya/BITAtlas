// src/features/navigation/components/MapToolbar.tsx

import React from "react";
import { Sliders, Compass, RotateCcw, Maximize2, Trash2, HelpCircle } from "lucide-react";

interface MapToolbarProps {
  onToggleLayers: () => void;
  onLocate: () => void;
  onResetView: () => void;
  onZoomToRoute?: () => void;
  onClearRoute?: () => void;
  routeActive: boolean;
}

export const MapToolbar: React.FC<MapToolbarProps> = ({
  onToggleLayers,
  onLocate,
  onResetView,
  onZoomToRoute,
  onClearRoute,
  routeActive
}) => {
  return (
    <div className="flex flex-col gap-1 bg-surface/90 border border-outline-variant/65 rounded-2xl p-1.5 shadow-2xl backdrop-blur-md max-w-[50px] items-center">
      {/* 1. Layers Drawer Toggle */}
      <button
        onClick={onToggleLayers}
        className="p-2 rounded-xl text-on-surface/60 hover:text-primary hover:bg-primary/10 transition duration-150 relative group"
        title="Map Layers & Legend"
        aria-label="Map Layers"
      >
        <Sliders className="w-4.5 h-4.5" />
        <span className="absolute right-full mr-2 top-1.5 bg-surface-variant border border-outline-variant rounded px-1.5 py-0.5 text-[9px] font-bold text-on-surface opacity-0 group-hover:opacity-100 transition whitespace-nowrap shadow-md pointer-events-none">
          Map Layers
        </span>
      </button>

      {/* 2. Locate User (Mock Locate) */}
      <button
        onClick={onLocate}
        className="p-2 rounded-xl text-on-surface/60 hover:text-primary hover:bg-primary/10 transition duration-150 relative group"
        title="Zoom to Campus Center"
        aria-label="Campus Center"
      >
        <Compass className="w-4.5 h-4.5" />
        <span className="absolute right-full mr-2 top-1.5 bg-surface-variant border border-outline-variant rounded px-1.5 py-0.5 text-[9px] font-bold text-on-surface opacity-0 group-hover:opacity-100 transition whitespace-nowrap shadow-md pointer-events-none">
          Center Campus
        </span>
      </button>

      {/* 3. Reset Camera Zoom */}
      <button
        onClick={onResetView}
        className="p-2 rounded-xl text-on-surface/60 hover:text-primary hover:bg-primary/10 transition duration-150 relative group"
        title="Reset Map Zoom"
        aria-label="Reset View"
      >
        <Maximize2 className="w-4.5 h-4.5" />
        <span className="absolute right-full mr-2 top-1.5 bg-surface-variant border border-outline-variant rounded px-1.5 py-0.5 text-[9px] font-bold text-on-surface opacity-0 group-hover:opacity-100 transition whitespace-nowrap shadow-md pointer-events-none">
          Reset View
        </span>
      </button>

      {/* 4. Zoom to Route */}
      {routeActive && onZoomToRoute && (
        <>
          <div className="h-px w-6 bg-outline-variant/35 my-1" />
          <button
            onClick={onZoomToRoute}
            className="p-2 rounded-xl text-primary hover:bg-primary/10 transition duration-150 relative group animate-bounce"
            title="Fit Route to Screen"
            aria-label="Zoom to Route"
          >
            <RotateCcw className="w-4.5 h-4.5 rotate-45" />
            <span className="absolute right-full mr-2 top-1.5 bg-surface-variant border border-outline-variant rounded px-1.5 py-0.5 text-[9px] font-bold text-on-surface opacity-0 group-hover:opacity-100 transition whitespace-nowrap shadow-md pointer-events-none">
              Zoom to Route
            </span>
          </button>
        </>
      )}

      {/* 5. Clear Route */}
      {routeActive && onClearRoute && (
        <button
          onClick={onClearRoute}
          className="p-2 rounded-xl text-error hover:bg-error/10 transition duration-150 relative group"
          title="Clear Active Route"
          aria-label="Clear Route"
        >
          <Trash2 className="w-4.5 h-4.5" />
          <span className="absolute right-full mr-2 top-1.5 bg-surface-variant border border-outline-variant rounded px-1.5 py-0.5 text-[9px] font-bold text-on-surface opacity-0 group-hover:opacity-100 transition whitespace-nowrap shadow-md pointer-events-none">
            Clear Route
          </span>
        </button>
      )}
    </div>
  );
};
export default MapToolbar;
