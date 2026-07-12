// src/features/navigation/components/RecentLocations.tsx

import React from "react";
import { History, Trash2, Compass } from "lucide-react";

interface RecentItem {
  id: string;
  name: string;
  type: string;
  latitude: number;
  longitude: number;
  timestamp: number;
}

interface RecentLocationsProps {
  recents: RecentItem[];
  onSelect: (item: RecentItem) => void;
  onNavigate: (item: RecentItem) => void;
  onClearAll: () => void;
}

export const RecentLocations: React.FC<RecentLocationsProps> = ({
  recents,
  onSelect,
  onNavigate,
  onClearAll
}) => {
  return (
    <div className="space-y-2 text-left">
      <div className="flex justify-between items-center pr-1">
        <p className="text-[9px] uppercase font-bold text-on-surface/40 tracking-wider">Search & Routing History</p>
        {recents.length > 0 && (
          <button
            onClick={onClearAll}
            className="text-[9px] font-bold text-error/65 hover:text-error hover:underline flex items-center gap-0.5"
          >
            <Trash2 className="w-2.5 h-2.5" />
            Clear
          </button>
        )}
      </div>

      {recents.length === 0 ? (
        <p className="text-xs text-on-surface/40 italic pl-1">No search history recorded.</p>
      ) : (
        <div className="space-y-1 max-h-40 overflow-y-auto pr-1 custom-scrollbar">
          {recents.map((item) => (
            <div
              key={`${item.id}-${item.timestamp}`}
              className="flex justify-between items-center p-1.5 rounded-xl hover:bg-surface-variant/25 transition group border border-transparent hover:border-outline-variant/30"
            >
              <button
                onClick={() => onSelect(item)}
                className="flex-1 text-left min-w-0 flex items-center gap-2"
              >
                <History className="w-3.5 h-3.5 text-on-surface/35 shrink-0" />
                <div className="min-w-0">
                  <p className="text-xs font-semibold text-on-surface/85 truncate">{item.name}</p>
                  <p className="text-[8px] text-on-surface/40 font-mono mt-0.5">{item.type}</p>
                </div>
              </button>

              <button
                onClick={() => onNavigate(item)}
                className="opacity-0 group-hover:opacity-100 p-1 text-primary hover:bg-primary/10 rounded-lg transition shrink-0"
                title="Navigate Here"
              >
                <Compass className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
export default RecentLocations;
