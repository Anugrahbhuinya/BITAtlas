// src/features/navigation/components/MiniInfoCard.tsx

import React from "react";
import { Compass, Eye, MapPin, Clock } from "lucide-react";
import type { Building, Facility, Landmark as LandmarkType } from "../types";

interface MiniInfoCardProps {
  entity: any;
  type: "building" | "facility" | "landmark";
  onNavigate: () => void;
  onViewDetails: () => void;
}

export const MiniInfoCard: React.FC<MiniInfoCardProps> = ({
  entity,
  type,
  onNavigate,
  onViewDetails
}) => {
  if (!entity) return null;

  const name = entity.building_name || entity.name || "";
  const category = entity.category || "";
  const code = entity.building_code || "";

  // Check if open/closed
  const getOpenStatus = () => {
    const hours = entity.opening_hours || entity.timing || "";
    if (!hours) return { text: "Open", color: "text-emerald-400 bg-emerald-500/10" };

    // Basic heuristic: check if typical 9:00 AM - 5:30 PM is open
    const now = new Date();
    const currentHour = now.getHours();
    
    if (currentHour >= 9 && currentHour < 18) {
      return { text: "Open Now", color: "text-emerald-400 bg-emerald-500/10" };
    }
    return { text: "Closed", color: "text-rose-400 bg-rose-500/10" };
  };

  const status = getOpenStatus();

  return (
    <div className="bg-surface/90 border border-outline-variant/65 rounded-2xl p-3 shadow-2xl backdrop-blur-md max-w-[240px] text-left select-none pointer-events-auto flex flex-col gap-2.5 animate-in fade-in slide-in-from-bottom-2 duration-150">
      <div>
        <div className="flex justify-between items-start gap-2">
          <span className="text-[8px] font-black uppercase tracking-wider px-1.5 py-0.5 rounded bg-primary/10 text-primary">
            {category || type}
          </span>
          <span className={`text-[8px] font-black uppercase px-1.5 py-0.5 rounded ${status.color}`}>
            {status.text}
          </span>
        </div>
        <h4 className="text-xs font-black text-on-surface mt-1.5 truncate">{name}</h4>
        {code && <p className="text-[8px] font-mono font-bold text-on-surface/40 uppercase mt-0.5">{code}</p>}
      </div>

      <div className="flex gap-1.5">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onNavigate();
          }}
          className="flex-1 py-1 px-2.5 bg-primary text-background hover:bg-primary/95 text-[10px] font-black rounded-lg transition flex items-center justify-center gap-1 shadow-sm"
        >
          <Compass className="w-3 h-3" />
          Go
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onViewDetails();
          }}
          className="py-1 px-2.5 bg-surface-variant/40 hover:bg-surface-variant/75 border border-outline-variant/40 text-on-surface/75 text-[10px] font-black rounded-lg transition flex items-center justify-center gap-1"
        >
          <Eye className="w-3 h-3" />
          Info
        </button>
      </div>
    </div>
  );
};
export default MiniInfoCard;
