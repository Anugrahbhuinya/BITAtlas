// src/features/navigation/components/LocationDetailsDrawer.tsx

import React, { useState, useEffect } from "react";
import { 
  X, MapPin, Clock, Phone, Accessibility, Landmark, Coffee, Users, Layers, Compass, Star, Share2, Check
} from "lucide-react";
import { useRooms } from "../hooks/useNavigation";
import type { Building, Room, Facility, Landmark as LandmarkType } from "../types";

interface LocationDetailsDrawerProps {
  entity: Building | Room | Facility | LandmarkType | null;
  entityType: "building" | "room" | "facility" | "landmark" | null;
  onClose: () => void;
  onSelectSubRoom?: (room: Room) => void;
  onGetDirections?: (entityId: string, name: string) => void;
  onSelectEntity?: (entity: any, type: "building" | "facility" | "landmark") => void;
  
  // Lists for calculating nearby services/buildings
  allBuildings?: Building[];
  allFacilities?: Facility[];
  allLandmarks?: LandmarkType[];
}

export const LocationDetailsDrawer: React.FC<LocationDetailsDrawerProps> = ({
  entity,
  entityType,
  onClose,
  onSelectSubRoom,
  onGetDirections,
  onSelectEntity,
  allBuildings = [],
  allFacilities = [],
  allLandmarks = []
}) => {
  const [isFavorite, setIsFavorite] = useState(false);
  const [copied, setCopied] = useState(false);

  // Sync favorite state
  useEffect(() => {
    if (!entity) return;
    const favs = localStorage.getItem("map_favorites");
    const favList = favs ? JSON.parse(favs) : [];
    setIsFavorite(favList.some((f: any) => f.id === entity._id));
  }, [entity]);

  if (!entity || !entityType) return null;

  // Toggle favorite
  const handleToggleFavorite = () => {
    const favs = localStorage.getItem("map_favorites");
    let favList = favs ? JSON.parse(favs) : [];
    const exists = favList.some((f: any) => f.id === entity._id);

    if (exists) {
      favList = favList.filter((f: any) => f.id !== entity._id);
      setIsFavorite(false);
    } else {
      const name = (entity as any).building_name || (entity as any).name || (entity as any).room_name || "";
      const type = entityType;
      const lat = entity.latitude || (entity as any).coordinates?.latitude || 0;
      const lng = entity.longitude || (entity as any).coordinates?.longitude || 0;
      favList.push({ id: entity._id, name, type, latitude: lat, longitude: lng });
      setIsFavorite(true);
    }

    localStorage.setItem("map_favorites", JSON.stringify(favList));
    // Notify sidebar
    window.dispatchEvent(new Event("favorites_changed"));
  };

  // Copy coordinates for sharing
  const handleShare = () => {
    const name = (entity as any).building_name || (entity as any).name || "";
    const lat = entity.latitude || (entity as any).coordinates?.latitude || 0;
    const lng = entity.longitude || (entity as any).coordinates?.longitude || 0;
    navigator.clipboard.writeText(`BIT Mesra Campus Navigation - ${name} (Lat: ${lat.toFixed(6)}, Lng: ${lng.toFixed(6)})`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Coordinate distance calculator in meters
  const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number) => {
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

  const lat = entity.latitude || (entity as any).coordinates?.latitude;
  const lng = entity.longitude || (entity as any).coordinates?.longitude;

  // Find 3 closest buildings
  const getNearbyBuildings = () => {
    if (!lat || !lng || allBuildings.length === 0) return [];
    return allBuildings
      .filter((b) => b._id !== entity._id)
      .map((b) => ({
        building: b,
        dist: calculateDistance(lat, lng, b.latitude, b.longitude)
      }))
      .sort((a, b) => a.dist - b.dist)
      .slice(0, 3);
  };

  const nearbyBuildings = getNearbyBuildings();

  // Render Building Details
  const RenderBuilding = ({ building }: { building: Building }) => {
    const { rooms, loading: roomsLoading } = useRooms(building._id);

    return (
      <div className="space-y-5">
        {/* Building Image Cover */}
        <div className="relative h-40 w-full rounded-2xl overflow-hidden bg-gradient-to-tr from-primary/30 to-secondary/30 border border-outline-variant/40 flex items-center justify-center">
          {building.image ? (
            <img src={building.image} alt={building.building_name} className="w-full h-full object-cover" />
          ) : (
            <div className="text-center space-y-1">
              <Layers className="w-10 h-10 text-primary/40 mx-auto animate-pulse" />
              <span className="text-[10px] uppercase font-black text-on-surface/40 tracking-wider">Campus Block</span>
            </div>
          )}
        </div>

        <div className="flex justify-between items-start text-left">
          <div>
            <span className="text-[10px] uppercase font-black tracking-wider px-2 py-0.5 bg-primary/10 text-primary border border-primary/20 rounded">
              {building.category}
            </span>
            <h2 className="text-xl font-black text-on-surface mt-1.5 leading-tight">{building.building_name}</h2>
            <p className="text-[10px] font-mono font-extrabold text-on-surface/45 uppercase mt-0.5">Code: {building.building_code}</p>
          </div>
          <button onClick={onClose} className="p-1 rounded-full hover:bg-surface-variant/40 text-on-surface/40 hover:text-on-surface transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        <p className="text-xs text-on-surface/75 leading-relaxed text-left">{building.description}</p>

        {/* Specs list */}
        <div className="grid grid-cols-2 gap-3 border-t border-b border-outline-variant/30 py-3 text-xs text-on-surface/70 text-left">
          <div className="flex items-center gap-1.5">
            <Clock className="w-4 h-4 text-primary shrink-0" />
            <span className="truncate">{building.opening_hours}</span>
          </div>
          {building.contact && (
            <div className="flex items-center gap-1.5">
              <Phone className="w-4 h-4 text-primary shrink-0" />
              <span className="truncate">{building.contact}</span>
            </div>
          )}
          <div className="flex items-center gap-1.5">
            <Layers className="w-4 h-4 text-primary shrink-0" />
            <span>Floors: {building.floors.join(", ")}</span>
          </div>
        </div>

        {/* Accessibility Panel */}
        <div className="bg-surface-variant/10 rounded-2xl p-4 border border-outline-variant/20 text-left">
          <h4 className="flex items-center gap-1.5 text-xs font-black text-on-surface mb-2">
            <Accessibility className="w-4 h-4 text-primary" />
            Accessibility Amenities
          </h4>
          <div className="flex flex-wrap gap-2 text-[10px] font-bold">
            <span className={`px-2 py-0.5 rounded ${building.accessibility.wheelchair_accessible ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20" : "bg-on-surface/5 text-on-surface/50"}`}>
              ♿ Wheelchair Access: {building.accessibility.wheelchair_accessible ? "Yes" : "No"}
            </span>
            <span className={`px-2 py-0.5 rounded ${building.accessibility.has_elevator ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20" : "bg-on-surface/5 text-on-surface/50"}`}>
              🛗 Elevator: {building.accessibility.has_elevator ? "Yes" : "No"}
            </span>
            <span className={`px-2 py-0.5 rounded ${building.accessibility.has_ramp ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20" : "bg-on-surface/5 text-on-surface/50"}`}>
              📈 Ramps: {building.accessibility.has_ramp ? "Yes" : "No"}
            </span>
          </div>
        </div>

        {/* Departments Panel */}
        {building.departments.length > 0 && (
          <div className="text-left">
            <h4 className="text-[10px] uppercase font-bold text-on-surface/40 tracking-wider mb-2">Departments Housed</h4>
            <div className="flex flex-wrap gap-1.5">
              {building.departments.map((dept, idx) => (
                <span key={idx} className="text-[11px] font-bold px-2.5 py-1 bg-surface-variant/40 border border-outline-variant/30 rounded-xl text-on-surface/75">
                  {dept}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Rooms inside Building */}
        <div className="text-left">
          <h4 className="text-[10px] uppercase font-bold text-on-surface/40 tracking-wider mb-2">Rooms inside building</h4>
          {roomsLoading ? (
            <p className="text-xs text-on-surface/50 animate-pulse">Loading rooms...</p>
          ) : (
            <div className="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto pr-1 custom-scrollbar">
              {rooms.map((room) => (
                <button
                  key={room._id}
                  onClick={() => onSelectSubRoom?.(room)}
                  className="p-2 border border-outline-variant/40 rounded-xl hover:bg-surface-variant/20 text-left transition"
                >
                  <p className="font-bold text-[11px] text-on-surface truncate">{room.room_number}</p>
                  <p className="text-[9px] text-on-surface/55 truncate">{room.room_name}</p>
                </button>
              ))}
              {rooms.length === 0 && (
                <p className="text-[10px] text-on-surface/40 col-span-2 italic">No rooms listed in this building.</p>
              )}
            </div>
          )}
        </div>
      </div>
    );
  };

  // Render Room Details
  const RenderRoom = ({ room }: { room: Room }) => {
    return (
      <div className="space-y-5 text-left">
        <div className="flex justify-between items-start">
          <div>
            <span className="text-[10px] uppercase font-black tracking-wider px-2 py-0.5 bg-secondary/10 text-secondary border border-secondary/20 rounded">
              {room.room_type}
            </span>
            <h2 className="text-xl font-bold text-on-surface mt-1.5 font-mono">{room.room_number}</h2>
            <p className="text-xs text-on-surface/60 mt-0.5">{room.room_name}</p>
          </div>
          <button onClick={onClose} className="p-1 rounded-full hover:bg-surface-variant/40 text-on-surface/40 hover:text-on-surface transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        <p className="text-xs text-on-surface/75 leading-relaxed">{room.description || "Room located inside campus block."}</p>

        <div className="grid grid-cols-2 gap-3 border-t border-b border-outline-variant/30 py-3 text-xs text-on-surface/70">
          <div className="flex items-center gap-1.5">
            <Users className="w-4 h-4 text-primary shrink-0" />
            <span>Capacity: {room.capacity} students</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Layers className="w-4 h-4 text-primary shrink-0" />
            <span>Floor: {room.floor}</span>
          </div>
        </div>

        {room.facilities.length > 0 && (
          <div>
            <h4 className="text-[10px] uppercase font-bold text-on-surface/40 tracking-wider mb-2">Room Amenities</h4>
            <div className="flex flex-wrap gap-1.5">
              {room.facilities.map((fac, idx) => (
                <span key={idx} className="text-[11px] font-bold px-2.5 py-1 bg-surface-variant/40 border border-outline-variant/30 rounded-xl text-on-surface/70">
                  {fac}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  // Render Facility Details
  const RenderFacility = ({ facility }: { facility: Facility }) => {
    return (
      <div className="space-y-5 text-left">
        <div className="flex justify-between items-start">
          <div>
            <span className="text-[10px] uppercase font-black tracking-wider px-2 py-0.5 bg-primary/10 text-primary border border-primary/20 rounded">
              {facility.category}
            </span>
            <h2 className="text-xl font-black text-on-surface mt-1.5">{facility.name}</h2>
          </div>
          <button onClick={onClose} className="p-1 rounded-full hover:bg-surface-variant/40 text-on-surface/40 hover:text-on-surface transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        <p className="text-xs text-on-surface/75 leading-relaxed">
          {facility.metadata?.description || "Campus service facility offering student support."}
        </p>

        <div className="flex items-center gap-1.5 text-xs text-on-surface/70 border-t border-b border-outline-variant/30 py-3">
          <Clock className="w-4 h-4 text-primary shrink-0" />
          <span>Hours: {facility.timing || "Open daily"}</span>
        </div>

        {facility.services.length > 0 && (
          <div>
            <h4 className="text-[10px] uppercase font-bold text-on-surface/40 tracking-wider mb-2">Services Provided</h4>
            <div className="flex flex-wrap gap-1.5">
              {facility.services.map((serv, idx) => (
                <span key={idx} className="text-[11px] font-bold px-2.5 py-1 bg-primary/5 border border-primary/20 rounded-xl text-primary">
                  ✓ {serv}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  // Render Landmark Details
  const RenderLandmark = ({ landmark }: { landmark: LandmarkType }) => {
    return (
      <div className="space-y-5 text-left">
        <div className="flex justify-between items-start">
          <div>
            <span className="text-[10px] uppercase font-black tracking-wider px-2 py-0.5 bg-secondary/10 text-secondary border border-secondary/20 rounded">
              {landmark.category}
            </span>
            <h2 className="text-xl font-black text-on-surface mt-1.5">{landmark.name}</h2>
          </div>
          <button onClick={onClose} className="p-1 rounded-full hover:bg-surface-variant/40 text-on-surface/40 hover:text-on-surface transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        <p className="text-xs text-on-surface/75 leading-relaxed">{landmark.description}</p>
        
        <div className="bg-surface-variant/10 rounded-2xl p-4 border border-outline-variant/20 flex gap-3 text-xs text-on-surface/70">
          <MapPin className="w-4 h-4 text-primary shrink-0" />
          <div>
            <span className="font-bold block">Location Coordinates</span>
            <span className="text-[10px] font-mono text-on-surface/50">Lat: {landmark.latitude}, Lng: {landmark.longitude}</span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="fixed md:absolute right-0 bottom-0 md:top-0 w-full md:w-96 max-h-[80vh] md:max-h-none md:h-full bg-background/90 border-t md:border-t-0 md:border-l border-outline-variant/65 shadow-2xl backdrop-blur-xl z-[4000] p-6 overflow-y-auto flex flex-col justify-between custom-scrollbar text-left">
      <div className="space-y-5 flex-1">
        {entityType === "building" && <RenderBuilding building={entity as Building} />}
        {entityType === "room" && <RenderRoom room={entity as Room} />}
        {entityType === "facility" && <RenderFacility facility={entity as Facility} />}
        {entityType === "landmark" && <RenderLandmark landmark={entity as LandmarkType} />}

        {/* Nearby Buildings Section */}
        {nearbyBuildings.length > 0 && onSelectEntity && (
          <div className="border-t border-outline-variant/30 pt-4 text-left">
            <h4 className="text-[10px] uppercase font-bold text-on-surface/40 tracking-wider mb-2">Nearby Buildings</h4>
            <div className="space-y-1.5">
              {nearbyBuildings.map(({ building: b, dist }) => (
                <button
                  key={b._id}
                  onClick={() => onSelectEntity(b, "building")}
                  className="w-full p-2 text-left bg-surface-variant/10 border border-outline-variant/25 rounded-xl hover:bg-surface-variant/30 flex justify-between items-center transition"
                >
                  <span className="text-xs font-bold text-on-surface truncate pr-2">{b.building_name}</span>
                  <span className="text-[9px] font-mono text-primary shrink-0 font-bold">{dist.toFixed(0)}m</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer controls: Navigate, Favorite, Share */}
      <div className="grid grid-cols-6 gap-2 border-t border-outline-variant/30 pt-4 mt-6">
        {/* Navigate Button */}
        {onGetDirections && (
          <button
            onClick={() => {
              const name = (entity as any).building_name || (entity as any).name || (entity as any).room_name || "";
              onGetDirections(entity._id, name);
            }}
            className="col-span-4 py-2.5 bg-primary text-background hover:bg-primary/95 text-xs font-black rounded-xl shadow-lg transition flex items-center justify-center gap-2"
          >
            <Compass className="w-4 h-4" />
            Get Directions
          </button>
        )}

        {/* Favorite Star Button */}
        <button
          onClick={handleToggleFavorite}
          className={`py-2.5 rounded-xl border flex items-center justify-center transition ${
            isFavorite 
              ? "bg-amber-400/10 border-amber-400/30 text-amber-400" 
              : "border-outline-variant/50 hover:bg-surface-variant/30 text-on-surface/60"
          }`}
          title={isFavorite ? "Remove from Favorites" : "Add to Favorites"}
        >
          <Star className={`w-4 h-4 ${isFavorite ? "fill-amber-400 text-amber-400" : ""}`} />
        </button>

        {/* Share Button */}
        <button
          onClick={handleShare}
          className={`py-2.5 rounded-xl border border-outline-variant/50 hover:bg-surface-variant/30 text-on-surface/60 flex items-center justify-center transition`}
          title="Share Coordinates"
        >
          {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Share2 className="w-4 h-4" />}
        </button>
      </div>
    </div>
  );
};
export default LocationDetailsDrawer;
