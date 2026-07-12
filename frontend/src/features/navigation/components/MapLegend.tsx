// src/features/navigation/components/MapLegend.tsx

import React from "react";
import { Landmark, HelpCircle, MapPin, Coffee, Home } from "lucide-react";

export const MapLegend: React.FC = () => {
  const items = [
    { label: "Academic", color: "bg-blue-500", icon: <MapPin className="w-3 h-3 text-white" /> },
    { label: "Administrative", color: "bg-purple-500", icon: <MapPin className="w-3 h-3 text-white" /> },
    { label: "Residential (Hostels)", color: "bg-emerald-500", icon: <Home className="w-3 h-3 text-white" /> },
    { label: "Point of Interest (POI)", color: "bg-amber-500", icon: <Landmark className="w-3 h-3 text-white" /> },
    { label: "Facilities (ATM/Xerox/OPD)", color: "bg-orange-500", icon: <Coffee className="w-3 h-3 text-white" /> },
  ];

  return (
    <div className="bg-surface/75 border border-outline-variant/60 rounded-xl p-3.5 shadow-lg backdrop-blur-md max-w-[220px]">
      <h5 className="text-[10px] uppercase font-bold tracking-wider text-on-surface/40 mb-2">Map Legend</h5>
      <div className="flex flex-col gap-2">
        {items.map((item, idx) => (
          <div key={idx} className="flex items-center gap-2 text-xs font-semibold text-on-surface/75">
            <div className={`flex items-center justify-center w-5 h-5 rounded-full ${item.color} shadow-sm shrink-0`}>
              {item.icon}
            </div>
            <span>{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
export default MapLegend;
