// src/features/navigation/components/LandmarkCard.tsx

import React from "react";
import { Landmark as LandmarkIcon } from "lucide-react";
import type { Landmark } from "../types";

interface LandmarkCardProps {
  landmark: Landmark;
  onFocusOnMap?: (landmark: Landmark) => void;
}

export const LandmarkCard: React.FC<LandmarkCardProps> = ({ landmark, onFocusOnMap }) => {
  const { name, category, description } = landmark;

  return (
    <div className="group relative overflow-hidden rounded-xl border border-outline-variant/60 bg-surface/40 p-4 transition-all duration-300 hover:border-primary/45 hover:bg-surface/50 hover:shadow-md">
      <div className="flex justify-between items-start mb-2">
        <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-secondary/10 text-secondary">
          {category}
        </span>
        <LandmarkIcon className="w-3.5 h-3.5 text-on-surface/30 group-hover:text-primary transition-colors" />
      </div>

      <h4 className="text-sm font-bold text-on-surface mb-1 group-hover:text-primary transition-colors">
        {name}
      </h4>

      <p className="text-xs text-on-surface/65 line-clamp-3 mb-3 leading-relaxed">
        {description || "No description available for this campus landmark."}
      </p>

      {onFocusOnMap && (
        <div className="flex justify-end pt-1 border-t border-outline-variant/20">
          <button
            onClick={() => onFocusOnMap(landmark)}
            className="text-[10px] font-bold text-primary hover:underline transition"
          >
            Locate on Map &rarr;
          </button>
        </div>
      )}
    </div>
  );
};
