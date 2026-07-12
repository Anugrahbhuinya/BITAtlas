// src/features/navigation/components/FacilityCard.tsx

import React from "react";
import { Clock, Briefcase, Check } from "lucide-react";
import type { Facility } from "../types";

interface FacilityCardProps {
  facility: Facility;
  onFocusOnMap?: (facility: Facility) => void;
}

export const FacilityCard: React.FC<FacilityCardProps> = ({ facility, onFocusOnMap }) => {
  const { name, category, timing, services, accessibility } = facility;

  return (
    <div className="group relative overflow-hidden rounded-xl border border-outline-variant/60 bg-surface/40 p-4 transition-all duration-300 hover:border-primary/45 hover:bg-surface/50 hover:shadow-md">
      <div className="flex justify-between items-start mb-2">
        <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-primary/10 text-primary">
          {category}
        </span>
        {accessibility.wheelchair_accessible && (
          <span className="text-xs" title="Wheelchair Accessible">♿</span>
        )}
      </div>

      <h4 className="text-sm font-bold text-on-surface mb-1 group-hover:text-primary transition-colors">
        {name}
      </h4>

      <div className="flex items-center gap-1 text-[11px] text-on-surface/70 mb-3">
        <Clock className="w-3.5 h-3.5 text-primary/75 shrink-0" />
        <span className="truncate">{timing || "Timings not specified"}</span>
      </div>

      {services.length > 0 && (
        <div className="mb-3 border-t border-outline-variant/30 pt-2.5">
          <p className="text-[9px] uppercase font-bold text-on-surface/45 tracking-wider mb-1.5">Services Provided</p>
          <div className="flex flex-wrap gap-1">
            {services.map((service, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-0.5 text-[9px] px-1.5 py-0.5 rounded-full bg-surface-variant/50 text-on-surface/85"
              >
                <Check className="w-2.5 h-2.5 text-primary shrink-0" />
                {service}
              </span>
            ))}
          </div>
        </div>
      )}

      {onFocusOnMap && (
        <div className="flex justify-end pt-1">
          <button
            onClick={() => onFocusOnMap(facility)}
            className="text-[10px] font-bold text-primary hover:underline transition"
          >
            Locate on Map &rarr;
          </button>
        </div>
      )}
    </div>
  );
};
