// src/features/navigation/components/MapContextMenu.tsx

import React, { useState, useEffect } from "react";
import { useMapEvents } from "react-leaflet";
import { MapPin, Navigation, Star, Copy, X } from "lucide-react";
import type { Building, Facility, Landmark as LandmarkType, GraphNode } from "../types";

interface MapContextMenuProps {
  buildings: Building[];
  facilities: Facility[];
  landmarks: LandmarkType[];
  allNodes: GraphNode[];
  onSetStart: (id: string, name: string) => void;
  onSetDestination: (id: string, name: string) => void;
  onViewDetails: (entity: any, type: "building" | "facility" | "landmark") => void;
  onAddFavorite: (entity: any) => void;
}

export const MapContextMenu: React.FC<MapContextMenuProps> = ({
  buildings,
  facilities,
  landmarks,
  allNodes,
  onSetStart,
  onSetDestination,
  onViewDetails,
  onAddFavorite
}) => {
  const [pos, setPos] = useState<{ lat: number; lng: number; x: number; y: number } | null>(null);
  const [closestPOI, setClosestPOI] = useState<{ entity: any; type: "building" | "facility" | "landmark"; name: string; nodeId: string } | null>(null);

  const getDistance = (lat1: number, lon1: number, lat2: number, lon2: number) => {
    const R = 6371e3; // meters
    const phi1 = (lat1 * Math.PI) / 180;
    const phi2 = (lat2 * Math.PI) / 180;
    const deltaPhi = ((lat2 - lat1) * Math.PI) / 180;
    const deltaLambda = ((lon2 - lon1) * Math.PI) / 180;

    const a =
      Math.sin(deltaPhi / 2) * Math.sin(deltaPhi / 2) +
      Math.cos(phi1) * Math.cos(phi2) * Math.sin(deltaLambda / 2) * Math.sin(deltaLambda / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  };

  useMapEvents({
    contextmenu(e) {
      const lat = e.latlng.lat;
      const lng = e.latlng.lng;
      const x = e.containerPoint.x;
      const y = e.containerPoint.y;

      // Find closest POI within 60 meters
      let bestPOI: any = null;
      let bestType: "building" | "facility" | "landmark" = "building";
      let bestDist = 60.0; // max 60 meters threshold
      let bestName = "";

      buildings.forEach((b) => {
        const d = getDistance(lat, lng, b.latitude, b.longitude);
        if (d < bestDist) {
          bestDist = d;
          bestPOI = b;
          bestType = "building";
          bestName = b.building_name;
        }
      });

      facilities.forEach((f) => {
        const d = getDistance(lat, lng, f.latitude, f.longitude);
        if (d < bestDist) {
          bestDist = d;
          bestPOI = f;
          bestType = "facility";
          bestName = f.name;
        }
      });

      landmarks.forEach((l) => {
        const d = getDistance(lat, lng, l.latitude, l.longitude);
        if (d < bestDist) {
          bestDist = d;
          bestPOI = l;
          bestType = "landmark";
          bestName = l.name;
        }
      });

      if (bestPOI) {
        // Find corresponding graph node ID
        // Often node ID matches code or building _id
        const code = bestPOI.building_code || bestPOI.name || bestPOI._id;
        const matchingNode = allNodes.find(
          (n) =>
            n.id === bestPOI._id ||
            n.id === bestPOI.building_code ||
            n.name.toLowerCase().includes(bestName.toLowerCase())
        );

        setClosestPOI({
          entity: bestPOI,
          type: bestType,
          name: bestName,
          nodeId: matchingNode?.id || bestPOI._id
        });
      } else {
        setClosestPOI(null);
      }

      setPos({ lat, lng, x, y });
    },
    click() {
      // Close context menu on left click anywhere on map
      setPos(null);
    }
  });

  if (!pos) return null;

  const handleCopyCoords = () => {
    navigator.clipboard.writeText(`${pos.lat.toFixed(6)}, ${pos.lng.toFixed(6)}`);
    setPos(null);
  };

  return (
    <div
      className="absolute bg-surface/95 border border-outline-variant/65 rounded-2xl shadow-2xl backdrop-blur-xl p-2.5 z-[5000] flex flex-col gap-1 text-left w-52"
      style={{
        left: `${pos.x}px`,
        top: `${pos.y}px`
      }}
    >
      <div className="flex justify-between items-center px-2 py-1 border-b border-outline-variant/30 mb-1.5">
        <span className="text-[9px] font-black uppercase text-on-surface/40 tracking-wider">
          {closestPOI ? closestPOI.name : "Custom Coordinate"}
        </span>
        <button onClick={() => setPos(null)} className="p-0.5 rounded-full hover:bg-surface-variant text-on-surface/40 hover:text-on-surface">
          <X className="w-3 h-3" />
        </button>
      </div>

      {closestPOI ? (
        <>
          <button
            onClick={() => {
              onSetStart(closestPOI.nodeId, closestPOI.name);
              setPos(null);
            }}
            className="flex items-center gap-2 px-2.5 py-1.5 rounded-xl hover:bg-primary/10 text-xs font-bold text-on-surface/85 hover:text-primary transition"
          >
            <Navigation className="w-3.5 h-3.5" />
            Set as Start
          </button>
          <button
            onClick={() => {
              onSetDestination(closestPOI.nodeId, closestPOI.name);
              setPos(null);
            }}
            className="flex items-center gap-2 px-2.5 py-1.5 rounded-xl hover:bg-primary/10 text-xs font-bold text-on-surface/85 hover:text-primary transition"
          >
            <MapPin className="w-3.5 h-3.5" />
            Set as Destination
          </button>
          <button
            onClick={() => {
              onViewDetails(closestPOI.entity, closestPOI.type);
              setPos(null);
            }}
            className="flex items-center gap-2 px-2.5 py-1.5 rounded-xl hover:bg-primary/10 text-xs font-bold text-on-surface/85 hover:text-primary transition"
          >
            <MapPin className="w-3.5 h-3.5 text-secondary" />
            View Details
          </button>
          <button
            onClick={() => {
              onAddFavorite(closestPOI.entity);
              setPos(null);
            }}
            className="flex items-center gap-2 px-2.5 py-1.5 rounded-xl hover:bg-primary/10 text-xs font-bold text-on-surface/85 hover:text-primary transition"
          >
            <Star className="w-3.5 h-3.5 text-amber-400" />
            Add to Favorites
          </button>
        </>
      ) : (
        <p className="text-[10px] text-on-surface/45 italic px-2 py-1 leading-normal">
          Click near a building or facility marker to select starting / ending navigation paths.
        </p>
      )}

      <div className="h-px bg-outline-variant/35 my-1" />

      <button
        onClick={handleCopyCoords}
        className="flex items-center gap-2 px-2.5 py-1.5 rounded-xl hover:bg-primary/10 text-xs font-bold text-on-surface/85 hover:text-primary transition"
      >
        <Copy className="w-3.5 h-3.5" />
        Copy Coordinates
      </button>
    </div>
  );
};
export default MapContextMenu;
