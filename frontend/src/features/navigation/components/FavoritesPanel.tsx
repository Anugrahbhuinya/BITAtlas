// src/features/navigation/components/FavoritesPanel.tsx

import React from "react";
import { Star, Compass, Trash2 } from "lucide-react";

interface FavoriteItem {
  id: string;
  name: string;
  type: string;
  latitude: number;
  longitude: number;
}

interface FavoritesPanelProps {
  favorites: FavoriteItem[];
  onSelect: (item: FavoriteItem) => void;
  onNavigate: (item: FavoriteItem) => void;
  onRemove: (id: string) => void;
}

export const FavoritesPanel: React.FC<FavoritesPanelProps> = ({
  favorites,
  onSelect,
  onNavigate,
  onRemove
}) => {
  return (
    <div className="space-y-2 text-left">
      {favorites.length === 0 ? (
        <p className="text-xs text-on-surface/40 italic pl-1">No favorite locations saved yet.</p>
      ) : (
        <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1 custom-scrollbar">
          {favorites.map((fav) => (
            <div
              key={fav.id}
              className="flex justify-between items-center p-2 rounded-xl bg-surface-variant/20 hover:bg-surface-variant/40 border border-outline-variant/30 hover:border-outline-variant/60 transition group"
            >
              <button
                onClick={() => onSelect(fav)}
                className="flex-1 text-left min-w-0"
              >
                <p className="text-xs font-bold text-on-surface truncate pr-2">{fav.name}</p>
                <p className="text-[9px] text-on-surface/40 uppercase tracking-wider font-extrabold font-mono mt-0.5">{fav.type}</p>
              </button>

              <div className="flex items-center gap-1.5 shrink-0 opacity-80 group-hover:opacity-100 transition">
                <button
                  onClick={() => onNavigate(fav)}
                  className="p-1 text-primary hover:bg-primary/10 rounded-lg transition"
                  title="Get Directions"
                >
                  <Compass className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => onRemove(fav.id)}
                  className="p-1 text-on-surface/45 hover:text-error hover:bg-error/10 rounded-lg transition"
                  title="Remove from Favorites"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
export default FavoritesPanel;
