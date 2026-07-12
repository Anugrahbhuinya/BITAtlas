// src/features/navigation/components/BuildingCard.tsx

import React from "react";
import { MapPin, Clock, ShieldCheck, ChevronRight, Eye } from "lucide-react";
import type { Building } from "../types";

interface BuildingCardProps {
  building: Building;
  onSelect?: (building: Building) => void;
  onFocusOnMap?: (building: Building) => void;
  isSelected?: boolean;
}

export const BuildingCard: React.FC<BuildingCardProps> = ({
  building,
  onSelect,
  onFocusOnMap,
  isSelected = false
}) => {
  const { building_name, building_code, category, departments, opening_hours, accessibility } = building;

  return (
    <div
      className={`group relative overflow-hidden rounded-xl border p-5 transition-all duration-300 backdrop-blur-md cursor-pointer ${
        isSelected
          ? "border-primary bg-primary/5 shadow-[0_0_15px_rgba(var(--color-primary-rgb),0.1)]"
          : "border-outline-variant/60 bg-surface/40 hover:border-primary/45 hover:bg-surface/60 hover:shadow-lg"
      }`}
      onClick={() => onSelect?.(building)}
    >
      <div className="flex justify-between items-start mb-2">
        <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-primary/10 text-primary">
          {category}
        </span>
        <span className="text-xs font-bold text-on-surface/40 font-mono group-hover:text-primary transition-colors">
          {building_code}
        </span>
      </div>

      <h3 className="text-base font-bold text-on-surface mb-1 group-hover:text-primary transition-colors">
        {building_name}
      </h3>

      <p className="text-xs text-on-surface/70 line-clamp-2 mb-4 leading-relaxed">
        {building.description || "No description available for this campus building."}
      </p>

      {departments.length > 0 && (
        <div className="mb-3">
          <p className="text-[10px] uppercase font-bold text-on-surface/40 tracking-wider mb-1">Departments</p>
          <div className="flex flex-wrap gap-1">
            {departments.slice(0, 3).map((dept, i) => (
              <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-surface-variant/40 border border-outline-variant/50 text-on-surface/75">
                {dept}
              </span>
            ))}
            {departments.length > 3 && (
              <span className="text-[10px] px-1.5 py-0.5 text-on-surface/50 font-medium">
                +{departments.length - 3} more
              </span>
            )}
          </div>
        </div>
      )}

      <div className="flex items-center justify-between border-t border-outline-variant/40 pt-3 text-[11px] text-on-surface/60">
        <div className="flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5 text-primary/75" />
          <span className="truncate max-w-[140px]">{opening_hours}</span>
        </div>
        <div className="flex gap-2 items-center">
          {accessibility.wheelchair_accessible && (
            <span className="text-primary" title="Wheelchair Accessible">♿</span>
          )}
          {onFocusOnMap && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onFocusOnMap(building);
              }}
              className="p-1 rounded bg-primary/10 text-primary hover:bg-primary hover:text-background transition duration-200"
              title="Show on Campus Map"
            >
              <Eye className="w-3.5 h-3.5" />
            </button>
          )}
          <ChevronRight className="w-4 h-4 text-on-surface/30 group-hover:text-primary group-hover:translate-x-0.5 transition-all" />
        </div>
      </div>
    </div>
  );
};
