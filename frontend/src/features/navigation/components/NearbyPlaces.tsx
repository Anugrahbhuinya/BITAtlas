// src/features/navigation/components/NearbyPlaces.tsx

import React from "react";
import { Coffee, Landmark, HelpCircle, Compass, MapPin } from "lucide-react";
import type { Building, Facility, Landmark as LandmarkType } from "../types";

interface NearbyPlacesProps {
  selectedEntity: any | null;
  buildings: Building[];
  facilities: Facility[];
  landmarks: LandmarkType[];
  onSelect: (entity: any, type: "building" | "facility" | "landmark") => void;
  onNavigate: (entity: any, name: string) => void;
}

export const NearbyPlaces: React.FC<NearbyPlacesProps> = ({
  selectedEntity,
  buildings,
  facilities,
  landmarks,
  onSelect,
  onNavigate
}) => {
  if (!selectedEntity) {
    return (
      <div className="p-4 bg-surface-variant/10 border border-outline-variant/35 rounded-2xl text-left">
        <p className="text-xs text-on-surface/40 italic">Select a campus location to explore nearby services.</p>
      </div>
    );
  }

  // Lat/Lng of selected entity
  const lat1 = selectedEntity.latitude || selectedEntity.coordinates?.latitude;
  const lon1 = selectedEntity.longitude || selectedEntity.coordinates?.longitude;

  if (!lat1 || !lon1) {
    return (
      <div className="p-4 bg-surface-variant/10 border border-outline-variant/35 rounded-2xl text-left">
        <p className="text-xs text-on-surface/40 italic">Unable to determine selected coordinates.</p>
      </div>
    );
  }

  // Haversine distance calculator in meters
  const calculateDistance = (lat2: number, lon2: number) => {
    const R = 6371e3; // meters
    const phi1 = (lat1 * Math.PI) / 180;
    const phi2 = (lat2 * Math.PI) / 180;
    const deltaPhi = ((lat2 - lat1) * Math.PI) / 180;
    const deltaLambda = ((lon2 - lon1) * Math.PI) / 180;

    const a =
      Math.sin(deltaPhi / 2) * Math.sin(deltaPhi/2) +
      Math.cos(phi1) *
        Math.cos(phi2) *
        Math.sin(deltaLambda / 2) *
        Math.sin(deltaLambda / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c; // meters
  };

  // Compile all entities with their computed distances
  const list: { entity: any; type: "building" | "facility" | "landmark"; distance: number; name: string; category: string }[] = [];

  buildings.forEach((b) => {
    if (b._id === selectedEntity._id) return;
    const dist = calculateDistance(b.latitude, b.longitude);
    list.push({ entity: b, type: "building", distance: dist, name: b.building_name, category: b.category });
  });

  facilities.forEach((f) => {
    if (f._id === selectedEntity._id) return;
    const dist = calculateDistance(f.latitude, f.longitude);
    list.push({ entity: f, type: "facility", distance: dist, name: f.name, category: f.category });
  });

  landmarks.forEach((l) => {
    if (l._id === selectedEntity._id) return;
    const dist = calculateDistance(l.latitude, l.longitude);
    list.push({ entity: l, type: "landmark", distance: dist, name: l.name, category: l.category });
  });

  // Sort by distance and take top 5 closest
  const nearbyItems = list.sort((a, b) => a.distance - b.distance).slice(0, 5);

  const getIcon = (category: string) => {
    const cat = category.toLowerCase();
    if (cat.includes("cafe") || cat.includes("canteen") || cat.includes("food")) {
      return <Coffee className="w-3.5 h-3.5 text-orange-400" />;
    } else if (cat.includes("atm") || cat.includes("bank")) {
      return <Landmark className="w-3.5 h-3.5 text-amber-400" />;
    }
    return <MapPin className="w-3.5 h-3.5 text-blue-400" />;
  };

  return (
    <div className="space-y-3 text-left">
      <div className="border-b border-outline-variant/30 pb-1">
        <p className="text-[9px] uppercase font-bold text-on-surface/40 tracking-wider">
          Nearby places from {selectedEntity.building_name || selectedEntity.name || "selected"}
        </p>
      </div>

      <div className="space-y-2">
        {nearbyItems.map((item, idx) => (
          <div
            key={`${item.entity._id}-${idx}`}
            className="flex justify-between items-center p-2 rounded-xl bg-surface-variant/10 hover:bg-surface-variant/30 border border-outline-variant/25 transition group"
          >
            <button
              onClick={() => onSelect(item.entity, item.type)}
              className="flex-1 text-left min-w-0 flex items-start gap-2.5"
            >
              <div className="p-1.5 rounded-lg bg-surface-variant/40 shrink-0 mt-0.5">
                {getIcon(item.category)}
              </div>
              <div className="min-w-0">
                <p className="text-xs font-bold text-on-surface/90 truncate">{item.name}</p>
                <p className="text-[9px] text-on-surface/50 font-semibold mt-0.5">
                  {item.category} • <span className="font-mono text-primary">{item.distance.toFixed(0)}m away</span>
                </p>
              </div>
            </button>

            <button
              onClick={() => onNavigate(item.entity, item.name)}
              className="opacity-0 group-hover:opacity-100 p-1.5 text-primary hover:bg-primary/10 rounded-lg transition shrink-0"
              title="Navigate Here"
            >
              <Compass className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}

        {nearbyItems.length === 0 && (
          <p className="text-xs text-on-surface/40 italic">No nearby services found.</p>
        )}
      </div>
    </div>
  );
};
export default NearbyPlaces;
